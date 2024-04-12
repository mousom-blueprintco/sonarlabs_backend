
import math
from typing import List, Tuple
from pydantic import BaseModel
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import fitz
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer, util
import requests
import base64
import os
import concurrent.futures
from sonarlabs_app.base.constants import OPENAI_API_KEY
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
class UserQuestion:
    def __init__(self, question):
        self.question = question

class BoundingBox:
    def __init__(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

class ResultPage:
    def __init__(self, page_num, match_percentage, image, bounding_boxes):
        self.page_num = page_num
        self.match_percentage = match_percentage
        self.image = image
        self.bounding_boxes = bounding_boxes

class ResponseResult:
    def __init__(self, response, result):
        self.response = response
        self.result = result

# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def sentence_similarity_check(sentence1, sentence2):
    prompt_1 = "Retrieve relevant passages that answer the given document search query:"
    prompt_2 = "Retrieve relevant passages from the provided document:"

    embedding_1 = model.encode(sentence1, convert_to_tensor=True, normalize_embeddings=True)
    embedding_2 = model.encode(sentence2, convert_to_tensor=True, normalize_embeddings=True)


    tensor_value = util.pytorch_cos_sim(embedding_1, embedding_2)
    similarity_perc = (math.pi - math.acos(tensor_value.item())) * 100 / math.pi
    return similarity_perc

def find_max_similarity(text, chunks):
    max_similarity = -1
    max_index = -1

    for i, chunk in enumerate(chunks):
        similarity = sentence_similarity_check(chunk, text)
        if similarity > max_similarity:
            max_similarity = similarity
            max_index = i

    if max_index != -1:
        return chunks[max_index], max_similarity
    else:
        return None, None

def highlight_text_on_page(page, page_text, texts, top_page_num, match_percentage, result):
    bounding_boxes = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        separators=['\n'],
        chunk_overlap=0,
        add_start_index=True
    )
    chunks = text_splitter.split_text(page_text)

    most_similar_sentence, max_similarity = find_max_similarity(texts, chunks)
    text_instances = page.search_for(most_similar_sentence, flags=2)

    for bbox in text_instances:
        highlight = page.add_highlight_annot(bbox)
        highlight.set_colors(stroke=[0.5, 1, 1])
        bounding_boxes.append(bounding_box_to_dict(BoundingBox(top=bbox[3], left=bbox[0], bottom=bbox[1], right=bbox[2])))
        highlight.update()
    img_bytes = page.get_pixmap().tobytes()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    # image = Image.open(io.BytesIO(img_bytes))
    # image.show()

    result.append({
        "page_num": top_page_num,
        "match_percentage": match_percentage,
        "image": img_base64,  # Use Base64 encoded string
        "bounding_boxes": bounding_boxes
    })
    bounding_boxes = []

def bounding_box_to_dict(bounding_box):
    return {
        "top": bounding_box.top,
        "left": bounding_box.left,
        "bottom": bounding_box.bottom,
        "right": bounding_box.right
    }

def get_uploaded_pdf_filename(file_url,file_id):
    pdf_content = requests.get(file_url).content
    file_name = f"{file_id}.pdf"
    with open(file_name, "wb") as temp_pdf:
            temp_pdf.write(pdf_content)

    return file_name

def get_pdf_chunks(file_name):
    result = []

    if len(result) > 0:
        result = []
    pdf_document = fitz.open(file_name)
    text = ""

    page_dict = {}

    for i, page in enumerate(pdf_document.pages()):
        page_content = page.get_text().lower()
        text += page_content + '\n\n'
        page_dict[page_content] = i+1

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    return chunks,page_dict,pdf_document,file_name,result

def open_ai_callback_response(chunks,user_question,file_name):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    faiss_index_path = f"faiss_index_{file_name}"
    
    if os.path.exists(faiss_index_path):
        
        db = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        # db = FAISS.load_local(faiss_index_path, embeddings)
    else:
        
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        
        knowledge_base.save_local(faiss_index_path)
        
        db = knowledge_base


    docs = db.similarity_search(user_question)
    prompt = """Given a document, answer a question about the document
    First validate if the question is really a true question, if not do a sementic search on the document and return exact information that is in the document.
    Do not include any other information. Only include the exact information that is
    in the document in the answer. Do not repharse the answer, keep it as it is in the document.
    If there is a question that cannot be answered, please say that there isn't enough information.

    Document: {context}

    Question: {query}
    """

    qa_prompt = ChatPromptTemplate.from_messages([("human", prompt)])
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, prompt=qa_prompt)
    with get_openai_callback() as cb:
        response = chain.invoke({"input_documents": docs, "query": user_question})
        print(f'billing details: {cb}')

        response = response['output_text'].replace("Answer:", "").strip()

    return response

def get_top_pages(page_dict,response):
        
        data = []
        for page_content, page_num in page_dict.items():
            similarity = sentence_similarity_check(response.lower(), page_content)
            data.append([similarity, page_num])

        data = sorted(data, key=lambda x: x[0], reverse=True)
        
        data_range =len(data)

        if data_range > 8:
            data_range = 8
        top_pages = [(data[i][1], round(data[i][0], 1)) for i in range(data_range)]

        return top_pages

def higlighted_data_result(top_pages,pdf_document,response,result):

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for top_page_num, match_percentage in top_pages:
            highlighted_page = pdf_document[top_page_num - 1]
            page = pdf_document.load_page(top_page_num - 1)
            page_text = page.get_text()
            if page_text:
                futures.append(executor.submit(highlight_text_on_page, highlighted_page, page_text, response, top_page_num, match_percentage, result))
        concurrent.futures.wait(futures)
    
    return result

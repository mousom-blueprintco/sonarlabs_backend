# import os
# import math
# from typing import List, Tuple
# # from fastapi import FastAPI, File, UploadFile
# from pydantic import BaseModel
# from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chains.question_answering import load_qa_chain
# from langchain.llms import OpenAI
# from langchain.callbacks import get_openai_callback
# import fitz
# from sentence_transformers import SentenceTransformer, util


# class UserQuestion(BaseModel):
#     question: str

# class BoundingBox(BaseModel):
#     top: float
#     left: float
#     bottom: float
#     right: float

# class ResultPage(BaseModel):
#     page_num: int
#     match_percentage: float
#     image: bytes
#     bounding_box: BoundingBox

# class ResponseResult(BaseModel):
#     response: str
#     result: List[ResultPage]

# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# def sentence_similarity_check(sentence1, sentence2):
#     prompt_1 = "Retrieve relevant passages that answer the given document search query:"
#     prompt_2 = "Retrieve relevant passages from the provided document:"

#     embedding_1 = model.encode(sentence1, convert_to_tensor=True, normalize_embeddings=True, prompt=prompt_1)
#     embedding_2 = model.encode(sentence2, convert_to_tensor=True, normalize_embeddings=True, prompt=prompt_2)

#     tensor_value = util.pytorch_cos_sim(embedding_1, embedding_2)
#     similarity_perc = (math.pi - math.acos(tensor_value.item())) * 100 / math.pi
#     return similarity_perc

# def find_max_similarity(text, chunks):
#     max_similarity = -1
#     max_index = -1

#     for i, chunk in enumerate(chunks):
#         similarity = sentence_similarity_check(chunk, text)
#         if similarity > max_similarity:
#             max_similarity = similarity
#             max_index = i

#     if max_index != -1:
#         return chunks[max_index], max_similarity
#     else:
#         return None, None

# def highlight_text_on_page(page, page_text, texts):
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         separators=['\n'],
#         chunk_overlap=0,
#         add_start_index=True
#     )
#     chunks = text_splitter.split_text(page_text)

#     most_similar_sentence, max_similarity = find_max_similarity(texts, chunks)
#     print(most_similar_sentence, max_similarity)
#     text_instances = page.search_for(most_similar_sentence, flags=2)
#     print(text_instances)
#     for bbox in text_instances:
#         highlight = page.add_highlight_annot(bbox)
#         highlight.set_colors(stroke=[0.5, 1, 1])
#         highlight.update()

# @app.post("/upload/")
# async def upload_pdf(user_question: UserQuestion, file: UploadFile = File(...)):

#     contents = await file.read()
#     with open("temp.pdf", "wb") as temp_pdf:
#         temp_pdf.write(contents)

#     pdf_document = fitz.open("temp.pdf")
#     text = ""

#     page_dict = {}
#     for i, page in enumerate(pdf_document.pages()):
#         page_content = page.get_text().lower()
#         text += page_content + '\n\n'
#         page_dict[page_content] = i+1

#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=500,
#         chunk_overlap=100,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(text)

#     embeddings = OpenAIEmbeddings(openai_api_key='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')
#     knowledge_base = FAISS.from_texts(chunks, embeddings)

#     user_question_text = user_question.question
#     docs = knowledge_base.similarity_search(user_question_text)

#     llm = OpenAI(openai_api_key='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')
#     chain = load_qa_chain(llm)
#     with get_openai_callback() as cb:
#         response = chain.run(input_documents=docs, question=user_question_text)
#         print(f'billing details: {cb}')

#     data = []
#     for page_content, page_num in page_dict.items():
#         similarity = sentence_similarity_check(response.lower(), page_content)
#         data.append([similarity, page_num])

#     data = sorted(data, key=lambda x: x[0], reverse=True)

#     top_pages = [(data[i][1], round(data[i][0], 1)) for i in range(8)]

#     result = []
#     for top_page_num, match_percentage in top_pages:
#         highlighted_page = pdf_document[top_page_num - 1]
#         page = pdf_document.load_page(top_page_num - 1)
#         page_text = page.get_text()
#         if page_text:
#             highlight_text_on_page(highlighted_page, page_text, response)
#             img_bytes = highlighted_page.get_pixmap().tobytes()
            
#             # Get bounding box coordinates
#             text_instances = highlighted_page.search_for(response)
#             bounding_boxes = []
#             for bbox in text_instances:
#                 bounding_boxes.append(BoundingBox(top=bbox[3], left=bbox[0], bottom=bbox[1], right=bbox[2]))
                
#             result.append({
#                 "page_num": top_page_num,
#                 "match_percentage": match_percentage,
#                 "image": img_bytes,
#                 "bounding_boxes": bounding_boxes
#             })

#     os.remove("temp.pdf")
#     return {"response": response, "result": result}
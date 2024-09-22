from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader, PDFPlumberLoader, PyPDFium2Loader, PyMuPDFLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_openai import OpenAIEmbeddings

def create_retriever(file_path, search_k):
    # 단계 1: 문서 로드(Load Documents)
    # loader = PDFMinerLoader(file_path)
    loader = PDFPlumberLoader(file_path)
    # loader = PyPDFium2Loader(file_path)
    # loader = PyMuPDFLoader(file_path)
    # loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # st.write(docs[37].page_content)
    # st.write(docs[37].metadata)
    

    # 단계 2: 문서 분할(Split Documents)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)
    # split_documents = docs

    # 단계 3: 임베딩(Embedding) 생성
    embeddings = OpenAIEmbeddings()

    # 단계 4: DB 생성(Create DB) 및 저장, # 벡터스토어를 생성합니다.
    faiss_vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    # 단계 5: 검색기(Retriever) 생성
    faiss_retriever = faiss_vectorstore.as_retriever(
        # search_type="similarity_score_threshold",  # 검색 유형을 "similarity_score_threshold 으로 설정        
        # search_kwargs={"score_threshold": threshold},  # 임계값 설정 및 검색 개수 설정
        search_kwargs={"k": search_k},
    )
    bm25_retriever = BM25Retriever.from_documents(split_documents)
    bm25_retriever.k = search_k


    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5])
    return ensemble_retriever
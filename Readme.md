IZU University RAG Chatbot - README
===================================

📋 Overview
-----------

This is a Retrieval-Augmented Generation (RAG) chatbot for Istanbul Sabahattin Zaim University. It answers questions about university programs, admissions, fees, and services in both Turkish and English.

🗂️ Project Structure
---------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   izu_scraper/  ├── chunking/  │   ├── all_data_cleaned_.jsonl     # Original cleaned data  │   ├── chunks.json                  # Chunked data (ready for RAG)  │   ├── embeddings_openai.npy        # Vector embeddings  │   ├── faiss_index.bin              # Vector database  │   ├── rag_config.json              # Configuration  │   ├── .env                         # API keys (DO NOT COMMIT!)  │   ├── chunking.ipynb               # Data preparation notebook  │   └── rag_system.ipynb             # RAG system notebook  └── README.md   `

🚀 Quick Start
--------------

### **Step 1: Prerequisites**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Python 3.8+ required  python --version  # Activate your virtual environment  source ~/rag-venv/bin/activate   `

### **Step 2: Install Dependencies**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install openai faiss-cpu numpy python-dotenv jupyter   `

### **Step 3: Setup OpenAI API Key**

Create a .env file in the chunking/ folder:

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cd ~/projects/izu_scraper/chunking  nano .env  ```  Add your OpenAI API key:  ```  OPENAI_API_KEY=sk-your-api-key-here   `

**Save and exit** (Ctrl+X, Y, Enter)

💬 How to Use
-------------

### **Option 1: Using Jupyter Notebook (Recommended)**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cd ~/projects/izu_scraper/chunking  jupyter notebook rag_system.ipynb   `

**Run the notebook cells in order:**

1.  Cell 1: Load chunks and setup
    
2.  Cell 8: Test the answer\_question() function
    

**Example usage in notebook:**

python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   result = answer_question("Yüksek lisans programları neler?")  print(result['answer'])   `

### **Option 2: Python Script**

Create a file chat.py:

python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   import json  import numpy as np  import faiss  import openai  from dotenv import load_dotenv  import os  # Setup  load_dotenv()  openai.api_key = os.getenv('OPENAI_API_KEY')  # Load resources  with open('chunks.json', 'r', encoding='utf-8') as f:      chunks = json.load(f)  index = faiss.read_index('faiss_index.bin')  def get_embedding(text):      response = openai.embeddings.create(          input=[text.replace("\n", " ")],          model="text-embedding-3-small"      )      return response.data[0].embedding  def retrieve_chunks(query, top_k=5):      query_embedding = np.array([get_embedding(query)], dtype='float32')      faiss.normalize_L2(query_embedding)      scores, indices = index.search(query_embedding, top_k)      results = []      for idx, score in zip(indices[0], scores[0]):          results.append({              'content': chunks[idx]['content'],              'metadata': chunks[idx]['metadata'],              'score': float(score)          })      return results  def answer_question(query):      # Retrieve      retrieved = retrieve_chunks(query, top_k=3)      # Build context      context = "\n---\n".join([          f"Kaynak: {c['metadata']['title']}\n{c['content']}"           for c in retrieved      ])      # Generate      response = openai.chat.completions.create(          model="gpt-4o-mini",          messages=[              {"role": "system", "content": "Sen İZÜ için bir asistansın. Sadece verilen bilgileri kullan."},              {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}          ],          temperature=0.3      )      return response.choices[0].message.content  # Use it  if __name__ == "__main__":      question = input("Sorunuz: ")      answer = answer_question(question)      print(f"\nCevap:\n{answer}")   `

**Run it:**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python chat.py   `

### **Option 3: Interactive Chat Script**

Create interactive\_chat.py:

python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   import json  import numpy as np  import faiss  import openai  from dotenv import load_dotenv  import os  # Setup (same as above)  load_dotenv()  openai.api_key = os.getenv('OPENAI_API_KEY')  with open('chunks.json', 'r', encoding='utf-8') as f:      chunks = json.load(f)  index = faiss.read_index('faiss_index.bin')  def get_embedding(text):      response = openai.embeddings.create(          input=[text.replace("\n", " ")],          model="text-embedding-3-small"      )      return response.data[0].embedding  def answer_question(query):      # Retrieve      query_embedding = np.array([get_embedding(query)], dtype='float32')      faiss.normalize_L2(query_embedding)      scores, indices = index.search(query_embedding, 3)      retrieved = [chunks[idx] for idx in indices[0]]      # Context      context = "\n---\n".join([          f"[{c['metadata']['title']}]\n{c['content']}"           for c in retrieved      ])      # Generate      response = openai.chat.completions.create(          model="gpt-4o-mini",          messages=[              {"role": "system", "content": "İZÜ asistanısın. Nazik ve profesyonel ol. Sadece verilen context'i kullan."},              {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}          ],          temperature=0.3      )      return response.choices[0].message.content  # Interactive loop  print("=" * 70)  print("İZÜ Chatbot - Hoş Geldiniz!")  print("=" * 70)  print("Çıkmak için 'exit' yazın\n")  while True:      question = input("💬 Siz: ")      if question.lower() in ['exit', 'quit', 'çıkış']:          print("Görüşmek üzere! 👋")          break      if not question.strip():          continue      print("🤖 Asistan: ", end="", flush=True)      answer = answer_question(question)      print(answer)      print()   `

**Run it:**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python interactive_chat.py   `

📝 Example Questions
--------------------

**Turkish:**

*   "Yüksek lisans programları neler?"
    
*   "Üniversite ücretleri ne kadar?"
    
*   "Burs imkanları var mı?"
    
*   "Kampüste yurt var mı?"
    
*   "Yabancı öğrenci başvurusu nasıl yapılır?"
    

**English:**

*   "What are the graduate programs?"
    
*   "What are the tuition fees?"
    
*   "Are there scholarships available?"
    
*   "How to apply as an international student?"
    

🔧 Troubleshooting
------------------

### **Error: No module named 'openai'**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install openai   `

### **Error: Invalid API key**

*   Check your .env file has the correct key
    
*   Make sure .env is in the chunking/ folder
    
*   Verify key format: OPENAI\_API\_KEY=sk-...
    

### **Error: File not found**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML``   # Make sure you're in the right directory  cd ~/projects/izu_scraper/chunking  ls  # Should see: chunks.json, faiss_index.bin, embeddings_openai.npy  ```  ### **Slow responses**  - Normal first time (loading models)  - Embeddings API: ~1-2 seconds  - GPT-4o-mini: ~2-5 seconds  - Total: ~3-7 seconds per question  ---  ## 💰 Cost Estimates  **Per 1000 questions (assuming avg 3 chunks retrieved):**  - Embeddings: ~$0.02  - GPT-4o-mini: ~$0.30  - **Total: ~$0.32 per 1000 questions**  Very affordable! 🎉  ---  ## 📊 System Performance  - **Retrieval time**: ~0.5 seconds  - **Generation time**: ~2-5 seconds  - **Total response time**: ~3-7 seconds  - **Accuracy**: High (uses actual university data)  - **Languages**: Turkish & English  ---  ## 🔐 Security Notes  ⚠️ **NEVER commit `.env` file to Git!**  Add to `.gitignore`:  ```  .env  *.npy  faiss_index.bin   ``

📚 Files Explanation
--------------------

FilePurposeSizechunks.jsonProcessed university data~5-20 MBembeddings\_openai.npyVector embeddings~50-200 MBfaiss\_index.binVector database~50-200 MBrag\_config.jsonConfiguration<1 KB.envAPI keys (secret!)<1 KB

🎯 Next Steps (Optional)
------------------------

1.  **Build Web Interface**: Create Streamlit/Gradio UI
    
2.  **Deploy**: Host on cloud (Heroku, Railway, AWS)
    
3.  **Add Features**:
    
    *   Conversation history
        
    *   Citation links
        
    *   Feedback system
        
    *   Analytics
        

🆘 Support
----------

**Issues?** Check:

1.  Virtual environment activated?
    
2.  API key set correctly in .env?
    
3.  All files present in chunking/ folder?
    
4.  OpenAI account has credits?
    

**Still stuck?** Check OpenAI API status: [https://status.openai.com/](https://status.openai.com/)

✅ Success Checklist
-------------------

*   Virtual environment activated
    
*   Dependencies installed
    
*   .env file created with API key
    
*   All files present (chunks.json, faiss\_index.bin, embeddings\_openai.npy)
    
*   Can run python chat.py successfully
    
*   Getting answers to test questions
    

**🎉 You're ready to use the RAG chatbot!**

**Quick test:**

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cd ~/projects/izu_scraper/chunking  python interactive_chat.py   `

Ask: "Üniversite hakkında bilgi ver" and see the magic! ✨
1. Install the requirements

    pip install -r requirements.txt

2. Also download nltk stopwords and punkt
   2.1 go to python terminal
   2.2 import nltk
   2.3 run command nltk.download("stopwords") and nltk.download("punkt")

3. Start the server using the router.py file :

    python router.py

4. Reload Model '/reload'

   {
	"kbid":"A1"
   }

5. predict label using the endpoint '/predict'

   {
	"question":"What is Global Entry Program (GEP)?",
	"kb_id":"A1",
	"top_n":2
	}


# -*- coding: utf-8 -*-

import sys
import os
import pickle
import json
import time

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
from queries import QueriesManager
from LexAnalyser import LexAnalyser
from PicklePersist import PicklePersist
from Retrievers import BooleanRetriever
from Postings import BinaryPostings
from Postings import SequentialPostings

def getParameters():
	# Obtengo Queries
	queriesFile = False
	try:
		if os.path.isfile(sys.argv[1]):
			queriesFile = sys.argv[1]
	except IndexError:
		queriesFile = False
	return queriesFile

def printRank(docsRank, documents):
	for q in docsRank:
		print "-" * 50
		print "Query:", q
		print "-" * 50
		if not docsRank[q]:
			print "Sin resultados"
		else:
			rank = 1
			for doc in docsRank[q]:
				print "Rank %d: %s" % (rank, documents.content[doc])
				rank += 1

def main():
	# Path en donde se encuentra la data indexada
	INDEX_DIR = "index_data/"
	
	# Chequeo que exista directorio
	if not os.path.exists(INDEX_DIR):
		print "ERROR: Para ejecutar este programa debe antes indexar una coleccion"
		sys.exit()

	# Cargo configuracion del index
	CONFIG_FILE= "config.json"
	config = json.load(open(INDEX_DIR + CONFIG_FILE))
	
	# Cargo index
	pp = PicklePersist()
	print "Cargando vocabulario"
	vocabulary = pp.load(INDEX_DIR+"vocabulary")
	print "Cargando documentos"
	documents = pp.load(INDEX_DIR+"documents")
	print "Cargando punteros a terminos"
	termToPointer = pp.load(INDEX_DIR+"term_to_pointer")	
	print "Cargando postings binarias"
	postings = BinaryPostings(INDEX_DIR+"binary_posting.dat", termToPointer)
	print "Cargando skipList"
	postings.setSkipLists(pp.load(INDEX_DIR+"skip_lists"))	
	print "Cargando postings secuenciales"
	seqPostings = SequentialPostings(INDEX_DIR+"seq_posting.txt")

	# Configuro al query manager
	la = LexAnalyser(config)
	qm = QueriesManager(booleanOperators=True)
	qm.setLexAnalyser(la)

	# Solicito queries
	queriesFile = getParameters()
	if queriesFile:
		qm.setQueriesFromTrecFile(queriesFile)
	else:
		qm.setQueriesFromConsole()

	# Realizo recuperacion
	if qm.queries:

		# Donde guardo tiempos de ejecucion de cada corrida
		times = {}

		# Postings secuenciales SIN skip lists
		br = BooleanRetriever(vocabulary, seqPostings, documents.content)
		startTime = time.time()
		print "-"*50
		print "RECUPERANDO: Postings Secuenciales SIN Skip Lists"
		br.retrieve(qm.queries)
		times["seqNoSl"] = time.time() - startTime
		print "-"*50

		# Postings binarias SIN skip lists
		br = BooleanRetriever(vocabulary, postings, documents.content)
		startTime = time.time()
		print "RECUPERANDO: Postings Binarias SIN Skip Lists"
		br.retrieve(qm.queries)
		times["binNoSl"] = time.time() - startTime
		print "-"*50

		# Postings binarias CON skip lists
		br = BooleanRetriever(vocabulary, postings, documents.content, skipLists=True)
		startTime = time.time()
		print "RECUPERANDO: Postings Binarias CON Skip Lists"
		br.retrieve(qm.queries)
		times["binSl"] = time.time() - startTime
		print "-"*50

		print "\n","-"*50
		print "Tiempos de ejecucion: "
		print "Postings Secuenciales SIN Skip Lists: ", times["seqNoSl"]
		print "Postings Binarias SIN Skip Lists: ", times["binNoSl"]
		print "Postings Binarias CON Skip Lists: ", times["binSl"]
		print "-"*50

if __name__ == "__main__":
	main()

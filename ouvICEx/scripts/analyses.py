import matplotlib.pyplot as plt
import datetime
import os
import glob
from flask import Flask, Blueprint, render_template, request, send_file
from scripts.database import posts, db

app_analyses = Blueprint("app_analyses", __name__, template_folder="templates")

def get_statistics(values, filtro, est):
	"""
		Agrupa o dado (values) por uma chave especificada (filtro), retornando
		o que é necessário para plotagem de gráficos.
		Args:
			values: iterável via query.all()
			filtro: filtro que servirá de base para agrupamento
		Return:
			labels: sticks do barplot
			totals: tamanhos das barras do barplot
	"""
	est = 0 if est == 'real' else 1 # alores possíveis de 'situation_t', realizadas (0) e apuradas (1)
	categories = ['ref_dep', 'author_dep', 'context_t', 'date'] # categorias possíveis de agrupamento
	dict_totals = {cat:{} for cat in categories} # cada categoria possui seu dicionário
	for vl in values: # para cada post soma 1 no dicionário de cada grupo na chave específica
		if vl.situation_t == est:
			if vl.ref_dep not in dict_totals['ref_dep'].keys(): # ref_dep
				dict_totals['ref_dep'][vl.ref_dep] = 1
			else:
				dict_totals['ref_dep'][vl.ref_dep] += 1
			if vl.author_dep not in dict_totals['author_dep'].keys(): # author_dep
				dict_totals['author_dep'][vl.author_dep] = 1
			else:
				dict_totals['author_dep'][vl.author_dep] += 1
			if vl.context_t not in dict_totals['context_t'].keys(): # context_t
				dict_totals['context_t'][vl.context_t] = 1
			else:
				dict_totals['context_t'][vl.context_t] += 1		
			if str(vl.date) not in dict_totals['date'].keys(): # date
				dict_totals['date'][str(vl.date)] = 1
			else:
				dict_totals['date'][str(vl.date)] += 1				
	
	# formata a saída para listas
	labels = list(dict_totals[filtro].keys())
	totals = list(dict_totals[filtro].values())
	
	return labels, totals

@app_analyses.route("/analyses", methods=["POST", "GET"])
def analyses():
	"""
		Função principal, avalia se trata-se de uma requisição ou não e 
		executa o respectivo randering.
	"""
	map_value_output = { # dicionário auxiliar para formatação de títulos
		'real': 'Total de denúncias realizadas',
		'apur': 'Total de denúncias apuradas',
		'date': 'Período',
		'ref_dep': 'Departamento',
		'context_t': 'Contexto'
	}
	
	if request.method == "GET": # se estiver apenas carregando a página
		grafico = "/static/graficos/empty.png" # cria um gráfico vazio
		titulo = ""
		figura = plt.scatter([], []) # produz o gráfico
		plt.savefig("ouvICEx" + grafico) # salva o gráfico
		plt.close()
		
		return render_template( # faz o rendering
			"analyses.html",
	 		values = posts.query.all(),
			grafico = grafico,
	 		titulo = titulo
		)
	elif request.method == "POST": # senão, se for o caso de requisição
		grafico = "/static/graficos/" # especifica o folder base das imagens
		est = str(request.form["est"]) # avalia qual estatística foi selecionada
		filt = str(request.form["filtro"]) # avalia qual filtro foi selecionado
		
		labels, totals = get_statistics(posts.query.all(), filt, est) # obtém os parâmetros para plotagem
			
		# executa formatações de título
		est = map_value_output[est]
		filt = map_value_output[filt]
		titulo = est + ' por ' + filt
		est = est.replace(' ', '_')
		filt = filt.replace(' ', '_')
		
		# produz e salva o gráfico
		#grafico += est + filt + ".png"
		grafico += str(datetime.datetime.now()).replace(" ", "_").replace(".", "__").replace(":", "___") + ".png"
		
		fig, ax = plt.subplots(1, 1)
		ax.bar(labels, totals, width = 0.5, color = 'grey')
		ax.set_xlim([None, 4])
		#figura = plt.bar(labels, totals, width = 0.5, color = 'grey')
		
		plt.xticks(rotation = 15)
		plt.savefig("ouvICEx" + grafico)
		plt.close()
		
		return render_template( # faz o rendering
			"analyses.html",
	 		values = posts.query.all(),
	 		grafico = grafico,
	 		titulo = titulo
		)
		

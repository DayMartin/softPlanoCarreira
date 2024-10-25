import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Progressbar
from datetime import datetime, timedelta
import json
import os

# Inicialização da lista para armazenar os objetivos
plano_de_carreira = []

# Função para salvar os dados em um arquivo JSON
def salvar_dados():
    with open('plano_de_carreira.json', 'w') as f:
        dados = []
        for objetivo in plano_de_carreira:
            dados.append({
                'objetivo': objetivo['objetivo'],
                'duracao': objetivo['duracao'],
                'acoes': objetivo['acoes'],
                'data_inicio': objetivo['data_inicio'].strftime('%Y-%m-%d'),
                'data_fim': objetivo['data_fim'].strftime('%Y-%m-%d'),
                'concluido': objetivo['concluido']
            })
        json.dump(dados, f)

# Função para carregar os dados ao iniciar a aplicação
def carregar_dados():
    if os.path.exists('plano_de_carreira.json') and os.path.getsize('plano_de_carreira.json') > 0:
        with open('plano_de_carreira.json', 'r') as f:
            try:
                dados = json.load(f)
                for dado in dados:
                    plano_de_carreira.append({
                        'objetivo': dado['objetivo'],
                        'duracao': dado['duracao'],
                        'acoes': dado['acoes'],
                        'data_inicio': datetime.strptime(dado['data_inicio'], '%Y-%m-%d'),
                        'data_fim': datetime.strptime(dado['data_fim'], '%Y-%m-%d'),
                        'concluido': dado['concluido']
                    })
                    lista_objetivos.insert(tk.END, dado['objetivo'])
            except json.JSONDecodeError:
                print("Erro ao decodificar o JSON. O arquivo pode estar corrompido.")


def adicionar_objetivo():
    objetivo = entrada_objetivo.get()
    duracao = int(entrada_duracao.get())
    acoes = entrada_acoes.get("1.0", tk.END)
    
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=duracao * 30)
    
    plano_de_carreira.append({
        'objetivo': objetivo,
        'duracao': duracao,
        'acoes': acoes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'concluido': False
    })
    
    lista_objetivos.insert(tk.END, objetivo)
    atualizar_progresso_geral()
    salvar_dados()

def exibir_detalhes(event):
    indice = lista_objetivos.curselection()
    if indice:
        indice = indice[0]
        objetivo = plano_de_carreira[indice]
        dias_restantes = (objetivo['data_fim'] - datetime.now()).days
        total_dias = (objetivo['data_fim'] - objetivo['data_inicio']).days
        progresso = (total_dias - max(dias_restantes, 0)) / total_dias * 100
        
        detalhes_text.delete("1.0", tk.END)
        detalhes_text.insert(tk.END, f"Objetivo: {objetivo['objetivo']}\n")
        detalhes_text.insert(tk.END, f"Duração: {objetivo['duracao']} meses\n")
        detalhes_text.insert(tk.END, f"Ações:\n{objetivo['acoes']}\n")
        detalhes_text.insert(tk.END, f"Data Início: {objetivo['data_inicio'].strftime('%d/%m/%Y')}\n")
        detalhes_text.insert(tk.END, f"Data Fim: {objetivo['data_fim'].strftime('%d/%m/%Y')}\n")
        detalhes_text.insert(tk.END, f"Dias Restantes: {dias_restantes} dias\n")
        
        progresso_unitario_bar['value'] = progresso
        if dias_restantes < 0:
            detalhes_text.insert(tk.END, "Atenção: o prazo terminou!\n")
            detalhes_text.tag_add("atraso", "end-2l", "end-1l")
            detalhes_text.tag_config("atraso", foreground="red")

def excluir_objetivo():
    indice = lista_objetivos.curselection()
    if indice:
        indice = indice[0]
        del plano_de_carreira[indice]
        lista_objetivos.delete(indice)
        detalhes_text.delete("1.0", tk.END)
        atualizar_progresso_geral()
        salvar_dados()

def concluir_objetivo():
    indice = lista_objetivos.curselection()
    if indice:
        indice = indice[0]
        plano_de_carreira[indice]['concluido'] = True
        atualizar_progresso_geral()
        salvar_dados()

def atualizar_progresso_geral():
    total_objetivos = len(plano_de_carreira)
    concluidos = sum(1 for obj in plano_de_carreira if obj['concluido'])
    
    if total_objetivos > 0:
        progresso_geral = (concluidos / total_objetivos) * 100
        progresso_geral_bar['value'] = progresso_geral

# Configuração da interface
root = tk.Tk()
root.title("Plano de Carreira")
root.geometry("800x400")

# Aplicando o estilo ttk
style = ttk.Style()
style.theme_use('clam')  # Alternativas: 'alt', 'default', etc.

# Frame principal horizontal
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame para entrada de dados
input_frame = ttk.Frame(main_frame)
input_frame.grid(row=0, column=0, sticky="nsew")

ttk.Label(input_frame, text="Objetivo:").grid(row=0, column=0)
entrada_objetivo = ttk.Entry(input_frame)
entrada_objetivo.grid(row=0, column=1)

ttk.Label(input_frame, text="Duração (meses):").grid(row=1, column=0)
entrada_duracao = ttk.Entry(input_frame)
entrada_duracao.grid(row=1, column=1)

ttk.Label(input_frame, text="Ações:").grid(row=2, column=0)
entrada_acoes = tk.Text(input_frame, height=5, width=30)
entrada_acoes.grid(row=2, column=1)

adicionar_button = ttk.Button(input_frame, text="Adicionar Objetivo", command=adicionar_objetivo)
adicionar_button.grid(row=3, column=1, pady=10)

# Frame para exibição de detalhes
display_frame = ttk.Frame(main_frame)
display_frame.grid(row=0, column=1, sticky="nsew", padx=10)

lista_objetivos = tk.Listbox(display_frame, height=10)
lista_objetivos.pack(side=tk.LEFT, fill=tk.Y)
lista_objetivos.bind('<<ListboxSelect>>', exibir_detalhes)

detalhes_text = tk.Text(display_frame, height=15, width=50)
detalhes_text.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

botao_frame = ttk.Frame(display_frame)
botao_frame.pack(pady=10)

excluir_button = ttk.Button(botao_frame, text="Excluir Objetivo", command=excluir_objetivo)
excluir_button.pack(side=tk.LEFT, padx=10)

concluir_button = ttk.Button(botao_frame, text="Concluir Objetivo", command=concluir_objetivo)
concluir_button.pack(side=tk.LEFT)

# Barra de progresso unitária
progresso_unitario_label = ttk.Label(display_frame, text="Progresso do Objetivo:")
progresso_unitario_label.pack()
progresso_unitario_bar = Progressbar(display_frame, length=300, mode='determinate')
progresso_unitario_bar.pack(pady=5)

# Barra de progresso geral
progresso_geral_label = ttk.Label(main_frame, text="Progresso Geral:")
progresso_geral_label.grid(row=1, column=0, columnspan=2, pady=10)
progresso_geral_bar = Progressbar(main_frame, length=600, mode='determinate')
progresso_geral_bar.grid(row=2, column=0, columnspan=2, pady=5)

# Carregar dados ao iniciar
carregar_dados()

# Salvar dados ao fechar
root.protocol("WM_DELETE_WINDOW", lambda: [salvar_dados(), root.destroy()])

root.mainloop()

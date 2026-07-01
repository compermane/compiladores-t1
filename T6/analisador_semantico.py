import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'antlr_gen'))
from antlr4 import *
from DOTA2Listener import DOTA2Listener
from DOTA2Parser import DOTA2Parser

HERO_DATABASE = {
    'antimage':         {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'axe':              {'ataque': 'melee',  'posicao': 3, 'alcance': 'melee'},
    'crystal_maiden':   {'ataque': 'ranged', 'posicao': 5, 'alcance': 'ranged'},
    'disruptor':        {'ataque': 'ranged', 'posicao': 5, 'alcance': 'ranged'},
    'drow_ranger':      {'ataque': 'ranged', 'posicao': 1, 'alcance': 'ranged'},
    'earthshaker':      {'ataque': 'melee',  'posicao': 4, 'alcance': 'melee'},
    'faceless_void':    {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'invoker':          {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
    'juggernaut':       {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'legion_commander': {'ataque': 'melee',  'posicao': 3, 'alcance': 'melee'},
    'lina':             {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
    'lion':             {'ataque': 'ranged', 'posicao': 5, 'alcance': 'ranged'},
    'magnus':           {'ataque': 'melee',  'posicao': 3, 'alcance': 'melee'},
    'morphling':        {'ataque': 'ranged', 'posicao': 1, 'alcance': 'ranged'},
    'ogre_magi':        {'ataque': 'melee',  'posicao': 4, 'alcance': 'melee'},
    'pa':               {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'phantom_assassin': {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'phantom_lancer':   {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'pudge':            {'ataque': 'melee',  'posicao': 3, 'alcance': 'melee'},
    'riki':             {'ataque': 'melee',  'posicao': 1, 'alcance': 'melee'},
    'rubick':           {'ataque': 'ranged', 'posicao': 4, 'alcance': 'ranged'},
    'sf':               {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
    'skywrath_mage':    {'ataque': 'ranged', 'posicao': 5, 'alcance': 'ranged'},
    'sniper':           {'ataque': 'ranged', 'posicao': 1, 'alcance': 'ranged'},
    'storm_spirit':     {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
    'tidehunter':       {'ataque': 'melee',  'posicao': 3, 'alcance': 'melee'},
    'tinker':           {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
    'vengeful_spirit':  {'ataque': 'ranged', 'posicao': 4, 'alcance': 'ranged'},
    'witch_doctor':     {'ataque': 'ranged', 'posicao': 5, 'alcance': 'ranged'},
    'zeus':             {'ataque': 'ranged', 'posicao': 2, 'alcance': 'ranged'},
}

ITEM_DATABASE = {
    'aghanims_scepter':  {'restricao': None},
    'assault_cuirass':   {'restricao': None},
    'battle_fury':       {'restricao': 'melee'},
    'black_king_bar':    {'restricao': None},
    'blink_dagger':      {'restricao': None},
    'bloodstone':        {'restricao': None},
    'daedalus':          {'restricao': None},
    'desolator':         {'restricao': None},
    'echo_sabre':        {'restricao': 'melee'},
    'force_staff':       {'restricao': None},
    'heart_of_tarrasque':{'restricao': None},
    'hurricane_pike':    {'restricao': 'ranged'},
    'magic_wand':        {'restricao': None},
    'manta_style':       {'restricao': None},
    'moon_shard':        {'restricao': None},
    'phase_boots':       {'restricao': None},
    'pipe_of_insight':   {'restricao': None},
    'power_treads':      {'restricao': None},
    'radiance':          {'restricao': 'melee'},
    'sange_and_yasha':   {'restricao': None},
    'shadow_blade':      {'restricao': None},
    'shivas_guard':      {'restricao': None},
    'silver_edge':       {'restricao': None},
    'skadi':             {'restricao': None},
    'soul_ring':         {'restricao': None},
}

MIDLANE_HEROES = {'lina', 'tinker', 'storm_spirit', 'invoker', 'zeus', 'sf'}
POS_NAMES = {1: "Hard Carry", 2: "Mid", 3: "Offlane", 4: "Soft Support", 5: "Hard Support"}


class AnalisadorSemantico(DOTA2Listener):
    def __init__(self):
        self.erros = []
        self.aliados = []
        self.rivais = []
        self.comandos = []
        self._linha_aliados = 0
        self._linha_rivais = 0

    def enterBloco_aliados(self, ctx):
        self._linha_aliados = ctx.COLON().getSymbol().line

    def enterBloco_rivais(self, ctx):
        self._linha_rivais = ctx.COLON().getSymbol().line

    def exitBloco_aliados(self, ctx):
        self.aliados = [id_.getText() for id_ in ctx.lista_herois().IDENT()]

    def exitBloco_rivais(self, ctx):
        self.rivais = [id_.getText() for id_ in ctx.lista_herois().IDENT()]

    def exitComando(self, ctx):
        if ctx.ANALISAR():
            heroi = ctx.IDENT(0).getText()
            linha = ctx.IDENT(0).getSymbol().line
            self.comandos.append(('analisar', heroi, linha))
        else:
            heroi = ctx.IDENT(0).getText()
            item = ctx.IDENT(1).getText()
            linha = ctx.IDENT(0).getSymbol().line
            self.comandos.append(('constroi', heroi, item, linha))

    def analisar(self):
        self._checar_existencia_herois(self.aliados)
        self._checar_existencia_herois(self.rivais)
        self._checar_unicidade_time(self.aliados, 'aliados')
        self._checar_unicidade_time(self.rivais, 'rivais')
        self._checar_duplicidade_entre_times()
        self._checar_limite_time(self.aliados, 'aliados')
        self._checar_limite_time(self.rivais, 'rivais')
        self._checar_composicao_aliados()
        self._checar_sinergia_magnus()
        self._checar_conflito_midlane()
        self._checar_comandos()
        return self.erros

    def _checar_existencia_herois(self, herois):
        for nome in herois:
            if nome not in HERO_DATABASE:
                linha = self._linha_aliados if nome in self.aliados else self._linha_rivais
                self.erros.append(f"Linha {linha}: heroi {nome} nao encontrado na base de dados")

    def _checar_unicidade_time(self, herois, escopo):
        vistos = {}
        for nome in herois:
            if nome in vistos:
                linha = self._linha_aliados if escopo == 'aliados' else self._linha_rivais
                self.erros.append(f"Linha {linha}: heroi {nome} repetido no time {escopo}")
            vistos[nome] = True

    def _checar_duplicidade_entre_times(self):
        for nome in self.rivais:
            if nome in self.aliados:
                self.erros.append(f"Linha {self._linha_rivais}: heroi {nome} ja foi escalado no time aliado")

    def _checar_limite_time(self, herois, escopo):
        if len(herois) > 5:
            linha = self._linha_aliados if escopo == 'aliados' else self._linha_rivais
            self.erros.append(f"Linha {linha}: time {escopo} excede o limite de 5 herois")

    def _checar_composicao_aliados(self):
        validos = [n for n in self.aliados if n in HERO_DATABASE]
        farm = sum(1 for n in validos if HERO_DATABASE[n]['posicao'] <= 3)
        suporte = sum(1 for n in validos if HERO_DATABASE[n]['posicao'] == 5)
        if farm > 3:
            self.erros.append(f"Linha {self._linha_aliados}: time aliado possui mais de 3 herois farm-dependentes")
        if suporte < 1:
            self.erros.append(f"Linha {self._linha_aliados}: time aliado nao possui suporte suficiente (minimo 1)")

    def _checar_sinergia_magnus(self):
        if 'magnus' in self.aliados:
            tem_melee = any(
                n in HERO_DATABASE and HERO_DATABASE[n]['alcance'] == 'melee' and n != 'magnus'
                for n in self.aliados
            )
            if not tem_melee:
                self.erros.append(f"Linha {self._linha_aliados}: magnus exige ao menos um aliado corpo a corpo")

    def _checar_conflito_midlane(self):
        presentes = [n for n in self.aliados if n in MIDLANE_HEROES]
        if len(presentes) >= 2:
            self.erros.append(f"Linha {self._linha_aliados}: conflito de rota - herois {', '.join(presentes)} disputam midlane")

    def _checar_comandos(self):
        for cmd in self.comandos:
            if cmd[0] == 'analisar':
                _, heroi, linha = cmd
                if heroi not in HERO_DATABASE:
                    self.erros.append(f"Linha {linha}: heroi {heroi} nao encontrado na base de dados")
            elif cmd[0] == 'constroi':
                _, heroi, item, linha = cmd
                if heroi not in HERO_DATABASE:
                    self.erros.append(f"Linha {linha}: heroi {heroi} nao encontrado na base de dados")
                    continue
                if item not in ITEM_DATABASE:
                    self.erros.append(f"Linha {linha}: item {item} nao encontrado na base de dados")
                    continue
                restricao = ITEM_DATABASE[item]['restricao']
                ataque = HERO_DATABASE[heroi]['ataque']
                if restricao and restricao != ataque:
                    if restricao == 'melee':
                        self.erros.append(f"Linha {linha}: item {item} incompativel com heroi {heroi} (restrito a corpo a corpo)")
                    else:
                        self.erros.append(f"Linha {linha}: item {item} incompativel com heroi {heroi} (restrito a distancia)")


def gerar_html(analisador):
    validos = [n for n in analisador.aliados if n in HERO_DATABASE]
    farm = [n for n in validos if HERO_DATABASE[n]['posicao'] <= 3]
    suporte = [n for n in validos if HERO_DATABASE[n]['posicao'] == 5]
    melee = [n for n in validos if HERO_DATABASE[n]['alcance'] == 'melee']
    ranged = [n for n in validos if HERO_DATABASE[n]['alcance'] == 'ranged']

    def cor_tipo(ataque):
        return '#4ade80' if ataque == 'melee' else '#60a5fa'

    def card_heroi(nome):
        h = HERO_DATABASE.get(nome)
        if not h:
            return f'<div class="hero-card unknown">{nome}</div>'
        cor = cor_tipo(h['ataque'])
        return f'''
        <div class="hero-card" style="border-left: 4px solid {cor};">
            <div class="hero-name">{nome}</div>
            <div class="hero-detail">Pos {h['posicao']} — {POS_NAMES[h['posicao']]}</div>
            <div class="hero-detail">{h['alcance']}</div>
        </div>'''

    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DOTA2Lang — Analise de Partida</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f0c29, #1a1a3e, #24243e);
    color: #e0e0e0;
    min-height: 100vh;
    padding: 20px;
}
.container { max-width: 1100px; margin: 0 auto; }
h1 {
    text-align: center;
    font-size: 2.2em;
    padding: 30px 0;
    background: linear-gradient(90deg, #ff6b35, #f7c948);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
h2 {
    color: #f7c948;
    margin: 25px 0 15px;
    font-size: 1.4em;
    border-bottom: 2px solid #333;
    padding-bottom: 8px;
}
.team-section {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
}
.team-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 15px;
}
.team-badge {
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.85em;
}
.badge-aliados { background: #1b5e20; color: #a5d6a7; }
.badge-rivais { background: #b71c1c; color: #ef9a9a; }
.hero-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
}
.hero-card {
    background: rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 14px;
    transition: transform 0.2s;
}
.hero-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.1); }
.hero-name { font-weight: bold; font-size: 1.1em; color: #fff; margin-bottom: 4px; }
.hero-detail { font-size: 0.85em; color: #aaa; margin-top: 2px; }
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 15px 0;
}
.stat-card {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-value { font-size: 2em; font-weight: bold; }
.stat-label { font-size: 0.85em; color: #aaa; margin-top: 4px; }
.stat-ok { color: #4ade80; }
.stat-fail { color: #f87171; }
.command-list { list-style: none; padding: 0; }
.command-item {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.95em;
}
.tag-ok {
    display: inline-block;
    background: #1b5e20; color: #a5d6a7;
    padding: 1px 8px; border-radius: 10px;
    font-size: 0.75em; margin-left: 8px;
}
.tag-fail {
    display: inline-block;
    background: #b71c1c; color: #ef9a9a;
    padding: 1px 8px; border-radius: 10px;
    font-size: 0.75em; margin-left: 8px;
}
.verdict {
    text-align: center; padding: 25px; margin: 25px 0;
    border-radius: 12px; font-size: 1.5em; font-weight: bold;
}
.verdict-ok {
    background: rgba(74, 222, 128, 0.15);
    border: 2px solid #4ade80; color: #4ade80;
}
.footer { text-align: center; color: #555; font-size: 0.8em; padding: 30px 0; }
</style>
</head>
<body>
<div class="container">
    <h1>DOTA2Lang — Análise da Partida</h1>'''

    html += '<div class="team-section">'
    html += '<div class="team-header"><span class="team-badge badge-aliados">ALIADOS</span></div>'
    html += '<div class="hero-grid">'
    for nome in analisador.aliados:
        html += card_heroi(nome)
    html += '</div></div>'

    html += '<div class="team-section">'
    html += '<div class="team-header"><span class="team-badge badge-rivais">RIVAIS</span></div>'
    html += '<div class="hero-grid">'
    for nome in analisador.rivais:
        html += card_heroi(nome)
    html += '</div></div>'

    html += '<h2>Análise Tática</h2>'
    farm_count = len(farm)
    sup_count = len(suporte)
    html += '<div class="stats-grid">'
    html += f'<div class="stat-card"><div class="stat-value {"stat-ok" if farm_count <= 3 else "stat-fail"}">{farm_count}/3</div><div class="stat-label">Farm-dependentes</div></div>'
    html += f'<div class="stat-card"><div class="stat-value {"stat-ok" if sup_count >= 1 else "stat-fail"}">{sup_count}</div><div class="stat-label">Suportes (pos 5)</div></div>'
    html += f'<div class="stat-card"><div class="stat-value">{len(melee)}</div><div class="stat-label">Corpo a corpo</div></div>'
    html += f'<div class="stat-card"><div class="stat-value">{len(ranged)}</div><div class="stat-label">Distancia</div></div>'
    html += '</div>'

    if 'magnus' in analisador.aliados:
        outros_melee = [n for n in melee if n != 'magnus']
        ok = len(outros_melee) > 0
        html += f'<div class="stat-card" style="margin:10px 0"><div class="stat-value {"stat-ok" if ok else "stat-fail"}">{"ATIVADA" if ok else "INATIVA"}</div><div class="stat-label">Sinergia Magnus (precisa de corpo a corpo)</div></div>'

    midlane_presentes = [n for n in validos if n in MIDLANE_HEROES]
    if midlane_presentes:
        ok = len(midlane_presentes) == 1
        html += f'<div class="stat-card" style="margin:10px 0"><div class="stat-value {"stat-ok" if ok else "stat-fail"}">{", ".join(midlane_presentes)}</div><div class="stat-label">Rota midlane</div></div>'

    if analisador.comandos:
        html += '<h2>Comandos</h2><ul class="command-list">'
        for cmd in analisador.comandos:
            if cmd[0] == 'analisar':
                _, heroi, _ = cmd
                if heroi in HERO_DATABASE:
                    html += f'<li class="command-item">analisar {heroi}</li>'
                else:
                    html += f'<li class="command-item">analisar {heroi} <span class="tag-fail">INVALIDO</span></li>'
            elif cmd[0] == 'constroi':
                _, heroi, item, _ = cmd
                if heroi in HERO_DATABASE and item in ITEM_DATABASE:
                    restricao = ITEM_DATABASE[item]['restricao']
                    ataque = HERO_DATABASE[heroi]['ataque']
                    if not restricao or restricao == ataque:
                        html += f'<li class="command-item">{heroi} constroi {item} <span class="tag-ok">EQUIPADO</span></li>'
                    else:
                        html += f'<li class="command-item">{heroi} constroi {item} <span class="tag-fail">INCOMPATIVEL</span></li>'
                elif heroi not in HERO_DATABASE:
                    html += f'<li class="command-item">{heroi} constroi {item} <span class="tag-fail">HEROI INVALIDO</span></li>'
                else:
                    html += f'<li class="command-item">{heroi} constroi {item} <span class="tag-fail">ITEM INVALIDO</span></li>'
        html += '</ul>'

    html += '<div class="verdict verdict-ok">Resultado: Partida viavel</div>'
    html += '</div></body></html>'
    return html

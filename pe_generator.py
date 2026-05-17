# pe_generator.py — génération du Plan d'Exécution via Grok IA
import json
from grok import Grok
from config import GROK_API_KEY, AI_MODEL

client = Grok(api_key=GROK_API_KEY)


def build_context(price: float, analyses: dict, htf_bias: dict) -> str:
    """Construit le contexte marché pour le prompt IA"""

    context = f"Prix actuel XAUUSD : {price}\n\n"
    context += f"BIAIS HTF GLOBAL : {htf_bias['bias']} (score: {htf_bias['score']})\n"
    context += "Détail des timeframes :\n"
    for line in htf_bias["details"]:
        context += f"  {line}\n"

    context += "\n--- ANALYSE PAR TIMEFRAME ---\n"

    for tf, analysis in analyses.items():
        if analysis.get("error"):
            continue

        context += f"\n[{tf}] Tendance: {analysis['trend']}\n"

        if analysis.get("bos"):
            bos = analysis["bos"]
            context += f"  BOS {bos['type']} @ {bos['level']}\n"

        if analysis.get("choch"):
            choch = analysis["choch"]
            context += f"  CHoCH {choch['type']} @ {choch['level']} — {choch['msg']}\n"

        if analysis.get("bullish_ob"):
            ob = analysis["bullish_ob"]
            context += f"  OB Bullish : {ob['bottom']} — {ob['top']} (mid: {ob['mid']})\n"

        if analysis.get("bearish_ob"):
            ob = analysis["bearish_ob"]
            context += f"  OB Bearish : {ob['bottom']} — {ob['top']} (mid: {ob['mid']})\n"

        if analysis.get("bullish_fvg"):
            fvg = analysis["bullish_fvg"]
            context += f"  FVG Bullish : {fvg['bottom']} — {fvg['top']}\n"

        if analysis.get("bearish_fvg"):
            fvg = analysis["bearish_fvg"]
            context += f"  FVG Bearish : {fvg['bottom']} — {fvg['top']}\n"

        if analysis.get("nearest_bsl"):
            context += f"  BSL (liquidité au-dessus) : {analysis['nearest_bsl']['level']}\n"

        if analysis.get("nearest_ssl"):
            context += f"  SSL (liquidité en-dessous) : {analysis['nearest_ssl']['level']}\n"

    return context


def generate_pe(price: float, analyses: dict, htf_bias: dict) -> dict:
    """Génère le Plan d'Exécution complet via IA"""

    context = build_context(price, analyses, htf_bias)

    prompt = f"""Tu es un trader expert ICT/SMC spécialisé sur XAUUSD.

Voici l'analyse technique complète du marché :

{context}

Sur la base de cette analyse, génère un Plan d'Exécution (PE) complet.
Réponds UNIQUEMENT en JSON valide avec cette structure :

{{
  "biais_global": "HAUSSIER ou BAISSIER ou NEUTRE",
  "resume_marche": "Résumé concis de la structure en 2-3 phrases",
  "scenario_principal": {{
    "direction": "LONG ou SHORT ou ATTENTE",
    "entree_zone": "ex: 2318-2322",
    "entree_type": "ex: OB H1 + FVG M15",
    "sl": "ex: 2310 (sous OB H1)",
    "tp1": "ex: 2335 (BSL M15)",
    "tp2": "ex: 2350 (BSL H1)",
    "rr": "ex: 1:3",
    "timing": "ex: Session London 08h-10h UTC"
  }},
  "scenario_alternatif": {{
    "condition": "Si le prix casse X...",
    "direction": "LONG ou SHORT",
    "zone": "ex: 2305-2308"
  }},
  "invalidation": "ex: Clôture H1 sous 2305",
  "niveaux_cles": ["2350 BSL H4", "2318 OB H1", "2305 SSL H1"],
  "patience": "ex: Attendre confirmation M15 avant entrée",
  "risque": "Faible ou Modéré ou Élevé"
}}

Réponds en français. Ne mets rien avant ou après le JSON."""

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Nettoyer si markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "biais_global": "N/A",
            "resume_marche": content,
            "scenario_principal": {},
            "scenario_alternatif": {},
            "invalidation": "",
            "niveaux_cles": [],
            "patience": "",
            "risque": "N/A"
        }
    except Exception as e:
        return {
            "biais_global": "ERREUR",
            "resume_marche": f"Erreur IA : {e}",
            "scenario_principal": {},
            "scenario_alternatif": {},
            "invalidation": "",
            "niveaux_cles": [],
            "patience": "",
            "risque": "N/A"
        }

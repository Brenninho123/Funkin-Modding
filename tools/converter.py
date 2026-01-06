import json
import sys
import os

# =========================
# Utilitários
# =========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =========================
# Conversor genérico
# =========================
def _convert_generic(data, source_name="Generic"):
    song = data.get("song", {})
    bpm = song.get("bpm", 120)
    speed = song.get("speed", 1)
    notes = song.get("notes", [])
    events = data.get("events", [])
    difficulties = data.get("difficulties", {"default": notes})

    crochet = 60000 / bpm
    step_crochet = crochet / 4
    section_time = step_crochet * 16  # 1 section = 16 steps

    def convert_notes(note_list):
        sections = {}
        for note in note_list:
            time = float(note.get("time", 0))
            lane = int(note.get("lane", 0))
            length = float(note.get("length", 0))
            must_hit = note.get("mustHit", True)
            note_type = note.get("type", "")

            section_index = int(time // section_time)
            if section_index not in sections:
                sections[section_index] = {
                    "sectionNotes": [],
                    "mustHitSection": must_hit,
                    "lengthInSteps": 16,
                    "sectionBeats": 4,
                    "changeBPM": False,
                    "bpm": bpm
                }

            psych_lane = lane if must_hit else lane + 4
            psych_note = [time, psych_lane, length, note_type]
            sections[section_index]["sectionNotes"].append(psych_note)
        return [sections[i] for i in sorted(sections.keys())]

    # Converter múltiplas dificuldades
    converted_diffs = {}
    for diff_name, diff_notes in difficulties.items():
        converted_diffs[diff_name] = convert_notes(diff_notes)

    # Converter events
    converted_events = []
    for ev in events:
        time = ev.get("time", 0)
        ev_type = ev.get("type", "")
        params = ev.get("params", [])
        converted_events.append([time, ev_type] + params)

    return {
        "song": {
            "song": song.get("name", f"converted_{source_name}"),
            "bpm": bpm,
            "speed": speed,
            "needsVoices": True,
            "player1": song.get("player1", "bf"),
            "player2": song.get("player2", "dad"),
            "gfVersion": song.get("gfVersion", "gf"),
            "stage": song.get("stage", "stage"),
            "notes": converted_diffs["default"],
            "events": converted_events,
            "difficulties": converted_diffs,
            "middlescroll": song.get("middlescroll", False)
        }
    }

# =========================
# Conversores específicos
# =========================
def convert_vslice(data): return _convert_generic(data, "V-Slice")
def convert_fnfc(data): return _convert_generic(data, "FNFC")
def convert_codename(data): return _convert_generic(data, "Codename")

# =========================
# Função principal
# =========================
def convert_chart(input_path, output_path, song_name=None, format_hint=None):
    data = load_json(input_path)

    # Detecta automaticamente pelo nome do arquivo
    if not format_hint:
        lower = input_path.lower()
        if "vslice" in lower: format_hint = "vslice"
        elif "fnfc" in lower: format_hint = "fnfc"
        elif "codename" in lower: format_hint = "codename"
        else: format_hint = "vslice"

    if format_hint.lower() == "vslice": psych_chart = convert_vslice(data)
    elif format_hint.lower() == "fnfc": psych_chart = convert_fnfc(data)
    elif format_hint.lower() == "codename": psych_chart = convert_codename(data)
    else: raise ValueError(f"Formato desconhecido: {format_hint}")

    if song_name: psych_chart["song"]["song"] = song_name

    save_json(output_path, psych_chart)
    print("✔ Conversão completa!")
    print(f"✔ Formato: {format_hint}")
    print(f"✔ Arquivo salvo em: {output_path}")

# =========================
# CLI
# =========================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python converter.py input.json output.json [songName] [format]")
        print("Formatos suportados: vslice | fnfc | codename")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    song_name_arg = sys.argv[3] if len(sys.argv) > 3 else None
    format_hint_arg = sys.argv[4] if len(sys.argv) > 4 else None

    convert_chart(input_file, output_file, song_name_arg, format_hint_arg)
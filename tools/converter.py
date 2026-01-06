import json
import sys
import os

# =========================
# Funções utilitárias
# =========================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =========================
# Conversores específicos
# =========================

def convert_vslice(data):
    return _convert_generic(data, "V-Slice")

def convert_fnfc(data):
    return _convert_generic(data, "FNFC")

def convert_codename(data):
    return _convert_generic(data, "Codename")

# Conversor genérico usado por todos
def _convert_generic(data, source_name="Generic"):
    song = data.get("song", {})
    bpm = song.get("bpm", 120)
    speed = song.get("speed", 1)
    notes = song.get("notes", [])

    crochet = 60000 / bpm
    step_crochet = crochet / 4
    section_time = step_crochet * 16  # 1 section = 16 steps

    sections = {}

    for note in notes:
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

        # Psych lane logic
        psych_lane = lane
        if not must_hit:
            psych_lane += 4

        psych_note = [
            time,
            psych_lane,
            length,
            note_type
        ]

        sections[section_index]["sectionNotes"].append(psych_note)

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
            "notes": [sections[i] for i in sorted(sections.keys())],
            "events": []
        }
    }

# =========================
# Função principal
# =========================

def convert_chart(input_path, output_path, song_name=None, format_hint=None):
    data = load_json(input_path)

    # Detect format automaticamente se possível
    if not format_hint:
        if "V-Slice" in input_path or "vslice" in input_path.lower():
            format_hint = "vslice"
        elif "fnfc" in input_path.lower():
            format_hint = "fnfc"
        elif "codename" in input_path.lower():
            format_hint = "codename"
        else:
            format_hint = "vslice"  # fallback

    if format_hint.lower() == "vslice":
        psych_chart = convert_vslice(data)
    elif format_hint.lower() == "fnfc":
        psych_chart = convert_fnfc(data)
    elif format_hint.lower() == "codename":
        psych_chart = convert_codename(data)
    else:
        raise ValueError(f"Formato desconhecido: {format_hint}")

    # Sobrescreve o nome da música se fornecido
    if song_name:
        psych_chart["song"]["song"] = song_name

    save_json(output_path, psych_chart)
    print("✔ Conversão concluída!")
    print(f"✔ Arquivo salvo em: {output_path}")
    print(f"✔ Formato detectado/forçado: {format_hint}")

# =========================
# CLI
# =========================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python converter.py input.json output.json [songName] [format]")
        print("format opcional: vslice | fnfc | codename")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    song_name_arg = sys.argv[3] if len(sys.argv) > 3 else None
    format_hint_arg = sys.argv[4] if len(sys.argv) > 4 else None

    convert_chart(input_file, output_file, song_name_arg, format_hint_arg)
import json
import sys

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def convert_vslice_to_psych(input_path, output_path, song_name="convertedSong"):
    data = load_json(input_path)

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

        # Psych lane: Player lanes 0-3, Opponent lanes 4-7
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

    psych_chart = {
        "song": {
            "song": song_name,
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

    save_json(output_path, psych_chart)
    print("✔ Conversão concluída!")
    print(f"Arquivo salvo em: {output_path}")

# CLI simples
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python converter.py input.json output.json [songName]")
        sys.exit(1)

    input_json = sys.argv[1]
    output_json = sys.argv[2]
    song_name = sys.argv[3] if len(sys.argv) > 3 else "convertedSong"

    convert_vslice_to_psych(input_json, output_json, song_name)

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load AI model (downloads once, then runs offline)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")


def load_movie_dialogues(path):
    characters = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                name, dialogue = line.split(":", 1)
                name = name.strip()
                dialogue = dialogue.strip()

                characters.setdefault(name, []).append(dialogue)

    # remove characters with very few dialogues
    characters = {k: v for k, v in characters.items() if len(v) >= 10}
    return characters


def load_chat_dialogues(path):
  lst_name_dialogue = {}
  names = []
  dialogues = []
  with open(path, "r",encoding="utf-8") as f:
    lines = f.readlines()
    length = len(lines)
    for i in range(length):
      line = lines[i].split("/202")

      if len(line) >= 2:
        line = line[1]
        index_i = line.index("-")
        line = line[index_i+1:]
        if ":" in line:
          ind_ = line.index(":")
          if "+91" not in line[0:ind_]:
            name = line[0:ind_]
          if name not in names: names.append(name)
          ind_name = names.index(name)


          dialogues.append([])
          if ("<Media omitted>") not in line[ind_+1:] :
            if "This message was deleted" not in line[ind_+1:]:
              if "You deleted this message" not in line[ind_+1:]:
                if "was edited" not in line[ind_+1:]:
                  if "http" not in line[ind_+1:]:
                    # if "\n" not in line[ind_+1:]:

                    dialogue = line[ind_+1:].split("\n")[0]

          dialogues[ind_name].append(dialogue)


    num_names = len(names)
    
    for i in range(num_names):
      lst_name_dialogue[names[i]] = dialogues[i]
  return lst_name_dialogue

  



def collapse_dialogues(d):
    return {k: " ".join(v) for k, v in d.items()}


def match_characters(chat_dl, movie_dl):
    chat_dl = collapse_dialogues(chat_dl)
    movie_dl = collapse_dialogues(movie_dl)

    chat_names = list(chat_dl.keys())
    movie_names = list(movie_dl.keys())

    chat_embeddings = model.encode(list(chat_dl.values()))
    movie_embeddings = model.encode(list(movie_dl.values()))

    similarity = cosine_similarity(chat_embeddings, movie_embeddings)

    mapping = {}

    while len(chat_names) > 0 and len(movie_names) > 0:
        i, j = np.unravel_index(np.argmax(similarity), similarity.shape)

        mapping[movie_names[j]] = chat_names[i]

        similarity = np.delete(similarity, i, 0)
        similarity = np.delete(similarity, j, 1)

        chat_names.pop(i)
        movie_names.pop(j)

    return mapping
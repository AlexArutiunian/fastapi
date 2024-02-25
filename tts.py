import re, os
import torch
import time
from pydub import AudioSegment

def txt_to_parts(text, i_max, j_max):
    parts = []
    idx = 0

    for _ in range(i_max * j_max):
        temp = "\n<speak>\n"
        remaining_text = text[idx:]

        first_period = remaining_text.find('.', 700)
        end_sentence = min(first_period + 1 if first_period != -1 else 750, len(remaining_text))

        temp += remaining_text[:end_sentence].replace('.', '.\n') + "\n</speak>\n"
        parts.append(temp)

        idx += end_sentence

        if idx >= len(text):
            break

    return parts


def delete_bad_sym(content):
    res = re.sub("[\'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]", "", content)
    return res


def lower_sym(text):
    text_out = text
    # unfortunatly .lower() does not work for russian lang

    lst_big_alp = dump_strfile_in_lst('storage/helpers/alpA.txt', [])
    lst_low_alp = dump_strfile_in_lst('storage/helpers/alp.txt', [])
    for elem1, elem2 in zip(lst_big_alp, lst_low_alp):
        text_out = replace_word_from_text(text_out, elem1, elem2)
    return text_out    


def add_plus_and_textnum(text):
    text_out = text
    lst1 = dump_strfile_in_lst('storage/helpers/word.txt', [])
    lst2 = dump_strfile_in_lst('storage/helpers/word+.txt', [])
    for elem1, elem2 in zip(lst1, lst2):

        # There is important spaces into the form: f" {elem1} "

        text_out = replace_word_from_text(text_out, f" {elem1} ", f" {elem2} ")

    return text_out    


def dump_strfile_in_lst(filename, lst):
    filename = os.path.abspath(filename)
    with open(f'{filename}', 'r', encoding="utf-8") as file:
        for line in file:
            lst.append(line.rstrip())
    return lst


def replace_word_from_text(text_in, before, after):
    text_out = text_in.replace(before, after)
    return text_out


def text_prepare(text, i_max):
    text_out = delete_bad_sym(text)
    text_out = lower_sym(text_out)

    text_out = replace_word_from_text(text_out, ",", " <s></s> ")
   
    text_out = replace_word_from_text(text_out, ")", " ) ")

    text_out = add_plus_and_textnum(text_out)

    parts = txt_to_parts(text_out, i_max, 3)

    for idx, item in enumerate(parts):
        parts[idx] = replace_word_from_text(item, ".", " <p></p> ")

    return parts


def TTS(text, model, path):

    ssml_sample = text
    sample_rate = 48000
    speaker='xenia'
    print(ssml_sample)
    audio_paths = model.save_wav(ssml_text=ssml_sample,
                                speaker=speaker,
                                sample_rate=sample_rate,
                                audio_path=path)


def delete_files_except_extension(extension, directory):
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            continue
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)            

def generate_sounds(text, name_audio_out):

    i_max = (int)(len(text) / 2100) + 1
    print("imax = ", i_max)
    test = text_prepare(text, i_max)
    for t in test:
        print(t)
    print(len(test))

     # Setup the system to generate speech from text trough 'model.pt' - SILERO_TTS

    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                                    local_file)

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)
   
    # Generate speeches from chuncks that are i_max * 3 (3 selected from an experiment)

    for i in range(0, len(test)):
        path = f"storage/gen_audio/sounds/{i}.wav"
        print(f"sounds/{i}")
        TTS(test[i], model, path=path)

    # Merge and save generated speeches

    path_ = "storage/gen_audio/sounds"
    lst = [f"{path_}/0.wav"]

    for i in range(1, len(test)):
      
        name = f"{path_}/{i}.wav"
        lst.append(name)   

        for audio in lst:
            print(audio)

    merge_ = AudioSegment.from_file(f"{path_}/0.wav", format="wav")
    for audio in lst:
        print(audio)
        sound = AudioSegment.from_file(audio, format="wav")
        merge_ += sound

    out_audio = f"output_audio"
    out_audio = os.path.abspath(out_audio)
    merge_.export(f"{out_audio}/{name_audio_out}.mp3", format="mp3")

    # delete temporary wav and txt of chuncks

    delete_files_except_extension(".md", "storage/gen_audio/sounds")   

    return merge_

if __name__ == "__main__":
    text_for_tts = "file.txt"
    with open(text_for_tts, "r", encoding="utf-8") as f:
        text = f.read()
        
    generate_sounds(text, "file")    
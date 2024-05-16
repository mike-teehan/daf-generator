# DAF Gen
Simple DAF (***D**elayed **A**uditory **F**eedback*) generator aimed at reducing stuttering.

## Screenshot
![Screenshot](screenshot.png?raw=true)

## Background
What's this all about:
  * [Delayed Auditory Feedback - Wikipedia](https://en.wikipedia.org/wiki/Delayed_Auditory_Feedback)
  * [Delayed Auditory Feedback - Wikibooks](https://en.wikibooks.org/wiki/Speech-Language_Pathology/Stuttering/Delayed_Auditory_Feedback)
  * [На волнах эффекта Ли: Питонизируем генерацию DAF / Хабр](https://habr.com/post/347580/)

## Building and requirements
DAF Gen is created via PySide6 framework and uses the PyAudio module for voice recording. All the necessary PIP dependencies are listed in *requirements.txt*.

## Platform requirements
### Linux
Ubuntu 22.04.4:
```
$ sudo apt install git build-essential python3-dev python3.10-venv portaudio19-dev
```

### Windows:
```
???
```

### MacOS:
```
???
```

## Build
Build with venv:
```
$ git clone https://github.com/mike-teehan/daf-generator.git
$ python3 -m venv daf-generator
$ cd daf-generator
$ . bin/activate
$ python3 -m pip install -r requirements.txt
```

## Run
Make sure the venv is already active, then run:
```
$ python3 dafgen.py
```

You can edit the Ui (**dafgen.ui**) with PyQt Designer as you like.  
After editing **dafgen.ui**, use **pyside3-uic** to rebuild **ui_dafgen.py** with your changes:
```
$ pyside6-uic dafgen.ui > ui_dafgen.py
```

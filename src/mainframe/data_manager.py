from tkinter import END, INSERT
from tkinter import SEL_FIRST, SEL_LAST
from tkinter import StringVar
import tkinter
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox

import os
import json


DEFAULT_DIR = "~/Documents"

PARAMS = "versificateur_params.json"


class DataManager:
    """
    Attach this to a text widget to interface with the data and parameters.

    The text widget must have all the methods of a TexFormattedText.
    """

    def __init__(self, textzone=None):
        """
        Loads parameters and the current file to the textzone
        that it is attached to.
        """
        self.cf = StringVar()
        self.cf.set("FICHIER :                     ")

        self.text = textzone
        self.load_params()
        if self.params["currentfile"]:
            self.open_file(self.params["currentfile"])


    def get_stringvar(self):
        """
        Gets a StringVar of the current behavior of the manager.
        """
        return self.cf

    def on_closing(self):
        """
        On closing, ask if the data must be saved.
        """
        if not self.params["currentfile"]:
            ok = messagebox.askokcancel('Données non sauvegardées',
                                   'Sauvegarder les données ?')
            if ok:
                self.on_save()
        else:
            self.on_save()
        self.save_params()

    def on_new(self, event=None):
        """
        When a new file is created, ask if the data must be saved.
        Then delete all the contents.
        """
        if self.text.get(1.0, END) != "":
            ok = messagebox.askokcancel('Données non sauvegardées',
                                   'Sauvegarder les données ?')
            if ok:
                self.on_save()
        self.text.delete('1.0', END)
        self.set_current_file(None)

    def on_open(self, event=None):
        """
        When asking to open a new file, ask if the data must be saved.
        Then delete all the contents.
        """
        if self.text.get(1.0, END) != "":
            ok = messagebox.askokcancel('Données non sauvegardées',
                                   'Sauvegarder les données ?')
            if ok:
                self.on_save()
                # return
        # else:
        filename = filedialog.askopenfilename(
                                initialdir=self.params["lastdir"],
                                defaultextension='.txt',
                                filetypes=(('Text files', '*.txt'),
                                                ('All files', '*.*')))
        if filename:
            self.text.delete('1.0', END)
            self.open_file(filename)

    def on_save(self, event=None):
        """
        Save the current file.
        """
        if self.params["currentfile"]:
            self.save_to_file(self.params["currentfile"])
        else:
            self.on_save_new()

    def on_save_new(self):
        """
        Save to a new file. First asks for this file, then
        created it and sets the current file to this file.
        """
        filename = filedialog.asksaveasfilename(
                                initialdir=self.params["lastdir"],
                                defaultextension='.txt',
                                filetypes=(('Text files', '*.txt'),
                                                ('All files', '*.*')))
        if filename:
            currentdir = os.path.dirname(filename)
            self.set_current_file(filename)
            self.save_to_file(filename)

    def on_export_tex(self):
        """
        Exports the contents of the text zone as a TeX file.
        """
        filename = filedialog.asksaveasfilename(
                                initialdir=self.params["lastdir"],
                                defaultextension='.txt',
                                filetypes=(('Tex files', '*.tex'),
                                                ('All files', '*.*')))
        if filename:
            with open(filename, 'w') as stream:
                # update the current working directory
                currentdir = os.path.dirname(filename)
                stream.write(self.text.export_tex())
                print("Exported tex code to file %s" % filename)

    def on_change_count(self):
        """
        Change the parameter regarding verse count.
        """
        newcount = simpledialog.askstring(
                                'Changer nombre de pieds',
                                'Sélectionnez un nombre de pieds',
                                initialvalue=self.params["compt"])
        try:
            self.params["compt"] = int(newcount)
        except Exception as e:
            print("Could not set a new verse count")

    #===============================

    def load_params(self):
        """
        Loads the parameters JSON file.
        """
        self.params = dict()
        self.params["lastdir"] = DEFAULT_DIR
        self.params["currentfile"] = None
        self.params["compt"] = 12
        try:
            currentdir = os.path.dirname(os.path.abspath(__file__))
            fpath = os.path.join(currentdir, PARAMS)
            with open(fpath, "r") as f:
                ob = json.load(f)
                if type(ob) == dict:
                # override the current and default parameters
                    for k in ob:
                        self.params[k] = ob[k]
        except Exception:
            print("Exception when trying to load parameters")

    def save_params(self):
        """
        Saves the parameters JSON file.
        """
        print("Saving parameters")
        try:
            currentdir = os.path.dirname(os.path.abspath(__file__))
            fpath = os.path.join(currentdir, PARAMS)
            with open(fpath, "w") as f:
                json.dump(self.params, f)
        except Exception as e:
            print("Could not save the parameters !")

    #====================================

    def set_current_file(self, filename):
        """
        Sets the current file (no file operation whatsoever here),
        only parameters and labels updating.
        """
        self.params["currentfile"] = filename
        if not filename:
            self.cf.set("FICHIER : Aucun")
        elif len(filename) > 20:
            self.cf.set("FICHIER : ...%s" % filename[-17:])
        else:
            self.cf.set("FICHIER : %s" % filename[-20:])

    def open_file(self, filename):
        """
        Opens a file.
        """
        try:
            with open(filename, 'r') as s:
                self.text.input_tex_with_comments(s.read())
                # self.text.input_formatted_text(s.read())
                self.set_current_file(filename)
        except Exception as e:
            print("Could not open file " + filename)
            self.set_current_file(None)
            print(e)


    def save_to_file(self, filename):
        """
        Saves to a file.
        """
        try:
            with open(filename, 'w') as stream:
                # update the current working directory
                currentdir = os.path.dirname(filename)
                self.params["lastdir"] = str(currentdir)
                stream.write(self.text.output_tex_with_comments().rstrip() + "\n")
                print("Contents have been saved to file %s" % filename)
        except Exception as e:
            print(e)
            print("Couldn't save to file %s" % filename)

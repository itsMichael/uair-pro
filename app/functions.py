
def lt(text, lang=""):
    """Return text in current language or in specified language"""
    from langs import langs
    try:
        text=text.encode("utf-8")
    except:pass
    #
    if not lang:
        from flask import session
        lang=session["lang"]
    #check language exists
    if lang not in langs.keys():
        lang="en"
    #check text
    if text not in langs[lang].keys():
        print("LANGS: translation not found: %s" % text)
        return text
    #return translated text
    ntext=langs[lang][text]
    try:
        ntext=ntext.decode("utf-8")
    except:pass
    return ntext

from geocongoai.text import saluer, introduire, dire_au_revoir


def test_saluer():
    assert saluer("Alice") == "Bonjour, Alice !"


def test_introduire():
    assert introduire("Bob", "développeur") == "Je m'appelle Bob et je suis développeur."


def test_dire_au_revoir():
    assert dire_au_revoir("Equipe") == "Au revoir, Equipe !"

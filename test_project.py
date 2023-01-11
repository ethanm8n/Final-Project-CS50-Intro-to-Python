import project
import pytest

def test_get_options():
	assert type(project.get_options()) is str

def test_books():
	with pytest.raises(TypeError):
		assert project.Books(-1)
	with pytest.raises(TypeError):
		assert project.Books(0)

def test_classify():
	b = project.Books(1).books
	assert type(project.classify(b)) is dict
	with pytest.raises(TypeError):
		assert project.classify(0)
	with pytest.raises(TypeError):
		assert project.classify(False)

def test_recommend():
	with pytest.raises(TypeError):
		assert project.recommend(0)
	with pytest.raises(TypeError):
		assert project.recommend(False)

def test_search():
	with pytest.raises(TypeError):
		assert project.recommend(0)
	with pytest.raises(TypeError):
		assert project.recommend(False)
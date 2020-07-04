rm -rf build dist json_to_swagger.egg-info
python3 setup.py sdist bdist_wheel
twine upload dist/*
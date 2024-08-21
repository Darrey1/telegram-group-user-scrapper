class Person:
    def __init__(self, name, school, age):
        self.name = name
        self.school = school
        self.age = age

value = Person(name="daretimileyin", school="futminna", age=23)

print(value.__dict__) 

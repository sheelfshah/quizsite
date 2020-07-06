"""
	format of txt file:	#no unnecessary spaces
		quiz title
		number of questions
		question title
		question text
		choice,choice,choice
		question title
		question text
		choice one,choice two,choice three
"""


def file_information_extract(f):
    quiz_title = f.readline().rstrip()
    print(quiz_title)
    num_q = int(f.readline())
    for _ in range(num_q):
        question_title = f.readline().rstrip()
        print(question_title)
        question_text = f.readline().rstrip()
        print(question_text)
        choices = f.readline().rstrip().split(',')
        print(choices)

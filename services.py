from models import Questionares

def get_by_questioner_id(questoner_id):
    questionnaire = Questionares.query.get_or_404(questoner_id)
    
    # Initialize the main structure for the response
    response_data = {
        'questionnaire': {
            'title': questionnaire.title,
            'description': questionnaire.description,
            'topic': questionnaire.topic,
            'total_audience': questionnaire.total_audience,
            'zdata': {
                'questions': []  # Create a list to hold question data
            }
        }
    }

    # Fetch questions related to the questionnaire
    questions = questionnaire.questions
    # questions = db.session.query(Question).filter(Question.questionarie_id == questoner_id).all()
    
    for question in questions:
        question_data = {
            'question_text': question.question_text,
            'rest': {
                'choices': [],
                'answers': []
            }
        }
        
        # Fetch choices for the question
        choices = question.choices
        # choices = db.session.query(Choices).filter(Choices.question_id == question.id).all()
        for choice in choices:
            question_data['rest']['choices'].append(choice.choice_text)

        # Fetch answers for the question
        answers = question.answers
        # answers = db.session.query(Answers).filter(Answers.question_id == question.id).all()
        for answer in answers:
            question_data['rest']['answers'].append({
                'email': answer.user.email,
                'name': answer.user.name,
                'answer': answer.answer
            })
        
        # Append the question data to the questionnaire data
        response_data['questionnaire']['zdata']['questions'].append(question_data)
        data =  response_data
        processed_data={
        "description":"",
        "title":"",
        "topic":"",
        "total_audience":0,
        "questions_and_answers":[]
        }
        questioner=data.get("questionnaire",{})
        processed_data["description"]=questioner.get("description","")
        processed_data["title"]=questioner.get("title","")
        processed_data["topic"]=questioner.get("topic","")
        processed_data["total_audience"]=questioner.get("total_audience",0)
        questions = questioner.get("zdata",{}).get("questions",[])

        for question in questions:
            question_text = question.get("question_text","")
            answers = question.get("rest",{}).get("answers",[])
            choices = question.get("rest",{}).get("choices",[])

            for answer in answers:
                answer_text = answer.get("answer","")
                email=answer.get("email","")
                name=answer.get("name","")
                processed_data["questions_and_answers"].append({
                "question": question_text,
                "answer": answer_text,
                "email": email,
                "name": name,
                "choices": choices
                })
    return processed_data
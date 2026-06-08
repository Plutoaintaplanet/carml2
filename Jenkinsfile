stage('Setup') {
steps {
bat '"C:\Users\admin\AppData\Local\Programs\Python\Python314\python.exe" -m pip install --upgrade pip setuptools wheel'
}
}

stage('Install Dependencies') {
steps {
bat '"C:\Users\admin\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt'
}
}

stage('Code Quality') {
steps {
bat '''
"C:\Users\admin\AppData\Local\Programs\Python\Python314\python.exe" -m pip install flake8
"C:\Users\admin\AppData\Local\Programs\Python\Python314\Scripts\flake8.exe" --max-line-length=120 CARML
'''
}
}

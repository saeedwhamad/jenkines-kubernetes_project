pipeline {
    agent any

    parameters {
     string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
     }

    stages {
        stage('Deploy') {
            steps {

                kubernetesDeploy(

                     configs: 'k8s/yolo5deployment.yaml',

                     kubeconfigId: 'my-kubeconfig'

                         )



            }
        }
    }
}
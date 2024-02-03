pipeline {
    agent any

    string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
    }

    stages {
        stage('Deploy') {
            steps {


                 kubernetesDeploy(

                     configs: 'k8s\polybot_pod.yaml',

                     kubeconfigId: 'my-kubeconfig'

                         )
            }
        }
    }
}
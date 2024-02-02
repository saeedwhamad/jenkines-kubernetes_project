pipeline {
    agent any
    stages{
        stage('Build') {
            steps {

                   sh '''
                    docker login -u saeedwh -p sa22edhama
                    docker image build -t yolok8s:${BUILD_NUMBER} ./DetectionBot/yolo5bot
                    docker tag yolok8s:${BUILD_NUMBER} saeedwh/yolok8s:${BUILD_NUMBER}
                    docker push saeedwh/yolok8s:${BUILD_NUMBER}
                      '''
            }

        }
        stage('Deploy to Kubernetes') {
            steps {
               sh "echo hi bye !"
                }

        }

     }
     post {
        success {
            echo 'Docker image built, pushed, and deployed successfully!'
        }

        failure {

            echo 'Docker image build, push, or deploy failed.'
        }
    }
}

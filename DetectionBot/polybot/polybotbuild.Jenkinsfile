pipeline {
    agent any
    stages{
        stage('Build') {
            steps {

                   cleanWs()
                   sh '''
                   echo hi
                    docker login -u saeedwh -p sa22edhama
                    docker image build -t polybotk8s:${BUILD_NUMBER} .
                    docker tag polybotk8s:${BUILD_NUMBER} saeedwh/polybotk8s:${BUILD_NUMBER}
                    docker push saeedwh/polybotk8s:${BUILD_NUMBER}

                      '''
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

import boto3
import json
from result_output import ResultOutput
import importlib.util
import sys, re
from decimal import Decimal
import requests, sqlite3

class Activity:
    test_passed = "Test Passed"
    test_failed = "Test Failed"

    User1_name='sarah'
    User2_name='meera'
    User1_group='dev'
    User2_group='prod'

    def testcase_check_for_user1_associated_to_group(self,session,test_object):
        testcase_description = "Check for the User sarah associated to dev group"
        reference = "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html"
        expected = "User1 {} associated to group {}".format(Activity.User1_name, Activity.User1_group)
        actual = "Sarah is NOT associated to Dev Group"
        test_object.update_pre_result(testcase_description,expected)
        try: 
            client = session.client('iam') 
            response = client.list_users()['Users']
            for name1 in response: 
                if name1['UserName']==Activity.User1_name:
                    response = client.list_groups_for_user(UserName=name1['UserName'])['Groups']
                    for name2 in response:
                        if name2['GroupName']==Activity.User1_group:
                            actual = "User1 {} associated to group {}".format(name1['UserName'], name2['GroupName'])
                            return test_object.update_result(1, expected, actual, Activity.test_passed, "N/A")                                                  
            return test_object.update_result(0, expected, actual, Activity.test_failed, reference)
        except Exception as e:    
            test_object.update_result(0, expected, actual, Activity.test_failed, reference)
            test_object.eval_message["testcase_check_for_user1_associated_to_group"] = str(e)

    def testcase_check_for_user2_associated_to_group(self,session,test_object):
        testcase_description = "Check for the User meera associated to prod group"
        reference = "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html"
        expected = "User2 {} associated to group {}".format(Activity.User2_name, Activity.User2_group)
        actual = "Meera is NOT associated to Prod Group"
        test_object.update_pre_result(testcase_description,expected)
        try: 
            client = session.client('iam') 
            response = client.list_users()['Users']
            for name1 in response: 
                if name1['UserName']==Activity.User2_name:
                    response = client.list_groups_for_user(UserName=name1['UserName'])['Groups']
                    for name2 in response:
                        if name2['GroupName']==Activity.User2_group:
                            actual = "User1 {} associated to group {}".format(name1['UserName'], name2['GroupName'])
                            return test_object.update_result(1, expected, actual, Activity.test_passed, "N/A")                                                  
            return test_object.update_result(0, expected, actual, Activity.test_failed, reference)
        except Exception as e:    
            test_object.update_result(0, expected, actual, Activity.test_failed, reference)
            test_object.eval_message["testcase_check_for_user2_associated_to_group"] = str(e) 

    def testcase_check_for_policy_attached_to_dev_group(self, session, test_object):
        testcase_description = "Check for policy attached to Dev group"
        reference = "https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-and-attach-iam-policy.html"
        expected = "AmazonEC2ReadOnlyAccess policy attached to Dev group"
        actual = "AmazonEC2ReadOnlyAccess is NOT attached to Dev group"
        test_object.update_pre_result(testcase_description,expected)
        try: 
            client = session.client('iam') 
            response = client.list_attached_group_policies(GroupName=Activity.User1_group)['AttachedPolicies']
            if len(response)==1:
                for name in response: 
                    if name['PolicyName']=='AmazonEC2ReadOnlyAccess':
                        actual="AmazonEC2ReadOnlyAccess policy attached to group {}".format(Activity.User1_group)
                        return test_object.update_result(1, expected, actual, Activity.test_passed, "N/A")                                                  
            return test_object.update_result(0, expected, actual, Activity.test_failed, reference)
        except Exception as e:    
            test_object.update_result(0, expected, actual, Activity.test_failed, reference)
            test_object.eval_message["testcase_check_service_creation"] = str(e)

    def testcase_check_for_policy_attached_to_prod_group(self, session, test_object):
        testcase_description = "Check for policy attached to Prod group"
        reference = "https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-and-attach-iam-policy.html"
        expected = "The 'GetBucketNotification' action is included in the IAM policy attached to the Prod group for a specific bucket"
        actual = "The 'GetBucketNotification' action is NOT included in the IAM policy attached to the Prod group for a specific bucket"
        test_object.update_pre_result(testcase_description,expected)
        try: 
            client = session.client('iam') 
            response = client.list_attached_group_policies(GroupName=Activity.User2_group)['AttachedPolicies']
            if len(response)==1:
                for name in response: 
                    if name['PolicyArn']:
                        response = client.get_policy_version(PolicyArn=name['PolicyArn'], VersionId='v1')
                        # Extract the policy document from the response
                        policy_document = response['PolicyVersion']['Document']
                        policy_statement=policy_document['Statement']
                        for action in policy_statement: 
                            if action['Action']=='s3:GetBucketNotification' and action['Resource'].split(':')[-1].startswith('s3learning'):
                                actual="Action {} is included in the IAM policy attached to the Prod group for a specific bucket {}".format(action['Action'], action['Resource'].split(':')[-1])
                                return test_object.update_result(1, expected, actual, Activity.test_passed, "N/A")                                                  
            return test_object.update_result(0, expected, actual, Activity.test_failed, reference)
        except Exception as e:    
            test_object.update_result(0, expected, actual, Activity.test_failed, reference)
            test_object.eval_message["testcase_check_for_policy_attached_to_prod_group"] = str(e)        
    
def start_tests(session, args):
    if "result_output" not in sys.modules:
        importlib.import_module("result_output")
    else:   
        importlib.reload(sys.modules["result_output"])
    test_object = ResultOutput(args,Activity)
    challenge_test = Activity()
    
    challenge_test.testcase_check_for_user1_associated_to_group(session, test_object)
    challenge_test.testcase_check_for_user2_associated_to_group(session, test_object)
    challenge_test.testcase_check_for_policy_attached_to_dev_group(session, test_object)
    challenge_test.testcase_check_for_policy_attached_to_prod_group(session, test_object)
    # challenge_test.testcase_check_for_number_of_tasks_creation(session, test_object)
    # challenge_test.testcase_check_task_creation(session, test_object)
    # challenge_test.testcase_check_for_public_ip_enabled_in_service_creation(session, test_object)

    json.dumps(test_object.result_final(), indent=4)
    print(test_object.result_final())
    return test_object.result_final()

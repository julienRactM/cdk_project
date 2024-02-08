from aws_cdk import (
    Stack
)
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import aws_cdk.aws_iam as iam

from aws_cdk import aws_elasticloadbalancing as elb
from aws_cdk import aws_elasticloadbalancingv2 as elbv2


from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_wafv2 as wafv2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import  aws_secretsmanager as secretsmanager


from aws_cdk import Stack
import aws_cdk.aws_stepfunctions as sfn


import aws_cdk as cdk

# sudo mysql -h cdkapp7stack-myec2dufutureinstance235426421312rdsi-uacnu9tvzezq.cy8mvqbyqx9z.us-east-1.rds.amazonaws.com -u julien -p

class CdkApp7Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        rds_security_group = ec2.SecurityGroup(self, "MyRDSdufutureInstance235426421312SecurityGroup",
            vpc=vpc,
            description="Allow inbound SSH, HTTP and MYSQL(3306) traffic",
            security_group_name="RDSdufutureSecurityGroup"
        )
        # rds_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")
        # rds_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")
        rds_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(3306), "MYSQL/Aurora")


        secret = rds.DatabaseSecret(self, "Presta_db0",
                username="julien"
        )

        rds_instance = rds.DatabaseInstance(self, "MyEC2dufutureInstance235426421312RDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0
            ),
            vpc=vpc,
            security_groups=[rds_security_group],
            removal_policy=cdk.RemovalPolicy.DESTROY,
            database_name="prestashop_db",
            publicly_accessible=True,
            credentials=rds.Credentials.from_secret(secret, 'julien'),
            allocated_storage=20,
            # storage_encrypted=True,  # Enable encryption at rest
            deletion_protection= False,
            instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                ec2.InstanceSize.MICRO),
        )

        proxy = rds.DatabaseProxy(self, "Proxy",
            # proxy_target=rds.ProxyTarget.from_cluster(rds_instance),
            proxy_target=rds.ProxyTarget.from_instance(rds_instance),
            secrets=[rds_instance.secret],
            # secrets=[proxy_secret],
            db_proxy_name = 'proxyPrestashop',
            vpc=vpc,
            security_groups=[rds_security_group],
            )

        ec2_security_group = ec2.SecurityGroup(self, "MyEC2dufutureInstance235426421312SecurityGroup",
            vpc=vpc,
            #rules
            description="Allow inbound SSH, and HTTP(S) traffic",
            security_group_name="EC2dufutureSecurityGroupV3",
            allow_all_outbound=True,
            disable_inline_rules=True
        )

        ec2_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")
        ec2_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")
        ec2_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'HTTPS')

        # Role ec2 --> proxy
        role = iam.Role(self, "EC2Full_AccessRDS",
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonRDSDataFullAccess')
            ]
        )

        # creating the alb's base, rules created after asg
        lb = elbv2.ApplicationLoadBalancer(self, "LB",
            vpc=vpc,
            # need to add a security group specific to elb/cdn later on for user
            internet_facing=True,
        )

        # web_acl = wafv2.CfnWebACL(
        #     self, "WAF_WAF",
        #     default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
        #     scope='REGIONAL',  # Set the scope to REGIONAL for ALB
        #     visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
        #         cloud_watch_metrics_enabled=True,
        #         metric_name="MyWebACLMetric",
        #         sampled_requests_enabled=True
        #     ),
        # )

        cloudfront_distribution = cloudfront.CloudFrontWebDistribution(
            self, "MyCloudFrontDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name=lb.load_balancer_dns_name,
                        origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ],
            # web_acl_id=web_acl.attr_id
            # webACLId=web_acl,
        )

        # from aws_cdk import aws_wafv2 as wafv2
        # cfnWebACLAssociation =  wafv2.CfnWebACLAssociation(self, 'MyCfnWebACLAssociation',
        #     CdnArn="",
        #     webAclArn= ""
        # )

        asg = autoscaling.AutoScalingGroup(self, "V7AutoScalingGroup3",
            vpc=vpc,
            # instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL),

            #prestashop already installed ami
            # machine_image=ec2.MachineImage.generic_linux(ami_map={'eu-west-3': ' ami-0886f7ba1137c73fa'}),
            ### CURRENT LATEST UBUNTU
            machine_image=ec2.MachineImage.generic_linux(ami_map={'eu-west-3': 'ami-01d21b7be69801c2f'}),


            security_group=ec2_security_group,
            role=role,
            min_capacity=2,
            max_capacity=4,
            desired_capacity=2,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            # here add again an user data with new_endpoint
            key_name="eu-west3N",
        )
        # not sure it does anything
        secret.grant_read(asg)


        listener = lb.add_listener("Listener",
            port=80,
            open=True
        )
        listener.add_targets("ApplicationFleet" ,
            port=8080,
            targets=[asg]
        )

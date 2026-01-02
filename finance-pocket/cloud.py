from unittest.mock import AsyncMagicMixin
from diagrams import Diagram, Cluster

from diagrams.aws.compute import EKS, EC2
from diagrams.aws.network import NLB, Route53, ALB
from diagrams.aws.database import Aurora, ElastiCache
from diagrams.aws.storage import S3
from diagrams.aws.general import Client
from diagrams.onprem.queue import Kafka, ActiveMQ


with Diagram("Finance Pocket Architecture", show=False, direction="TB", strict=True):
    nlb = NLB("Load Balancer")

    with Cluster("Services"):
        alb = ALB("Application Load Balancer")
        api = EKS("Backend Service")

        with Cluster("Background"):
            background = EC2("Worker Scheduler")
            mq = ActiveMQ("Message Queue")
            celery = EKS("Background Jobs (Interruptable)")

            background - mq
            mq - celery


    with Cluster("Data Layer"):
        with Cluster("Database", direction="TB"):
            db_primary = Aurora("primary")
            read_replica = Aurora("read replica")
            db_primary - read_replica

        cache = ElastiCache("Redis")
        kafka = Kafka("Kafka")
        storage = S3("Storage")

    Client("User") >> Route53("DNS") >> nlb >> alb >> api

    api >> kafka >> background

    celery >> read_replica
    celery >> db_primary

    api >> db_primary
    api >> cache
    api >> storage

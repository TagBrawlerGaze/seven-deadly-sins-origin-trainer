from sds_origin_trainer.pipeline.job import TrainerJob, JobState


def test_job_transitions_happy_path():
    job = TrainerJob(module="godmode", pid=1234)
    job.transition(JobState.ATTACHING)
    job.transition(JobState.RUNNING)
    job.transition(JobState.DONE)
    assert job.state is JobState.DONE


def test_job_rejects_illegal_transition():
    job = TrainerJob(module="inf_mana", pid=1234)
    try:
        job.transition(JobState.DONE)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
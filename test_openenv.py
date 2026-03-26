"""Test script for OpenEnv validation"""

from environment import EmailTriageEnv, Action

def test_environment():
    """Test all required OpenEnv methods"""
    env = EmailTriageEnv()
    
    # Test reset
    print("Testing reset()...")
    obs = env.reset(task_id=1)
    assert obs.task_id == 1
    assert len(obs.visible_emails) == 3
    print("✓ reset() works")
    
    # Test step
    print("\nTesting step()...")
    action = Action("mark_spam", 1)
    obs, reward, done, info = env.step(action)
    assert reward is not None
    print(f"✓ step() works - reward: {reward}")
    
    # Test state
    print("\nTesting state()...")
    state = env.state()
    assert "task_id" in state
    assert "actions_taken" in state
    print("✓ state() works")
    
    # Test grade
    print("\nTesting grade()...")
    grade = env.grade()
    assert 0.0 <= grade <= 1.0
    print(f"✓ grade() works - score: {grade}")
    
    print("\n" + "="*50)
    print("✅ All OpenEnv methods working correctly!")
    print("="*50)

if __name__ == "__main__":
    test_environment()

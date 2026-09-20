from app.config import RESUME_PATH
from app.intelligence.resume_intelligence import (
    ResumeIntelligence,
)


def main():
    print("=" * 70)
    print("REAL RESUME INTELLIGENCE TEST")
    print("=" * 70)

    engine = ResumeIntelligence(RESUME_PATH)

    profile = engine.build_profile()

    output = engine.save_profile(profile)

    assert profile["resume_path"] == RESUME_PATH
    assert profile["name"]
    assert profile["skills"]
    assert profile["roles"]

    print(f"\nResume      : {RESUME_PATH}")
    print(f"Profile     : {output}")
    print(f"Name        : {profile['name']}")
    print(f"Email       : {profile['email']}")
    print(f"Phone       : {profile['phone']}")
    print(
        f"Experience  : "
        f"{profile['experience_years']}"
    )

    print("\nRoles:")
    for role in profile["roles"]:
        print(f"  ✓ {role}")

    print("\nSkills:")
    for skill in profile["skills"]:
        print(f"  ✓ {skill}")

    print("\nEducation:")
    for item in profile["education"]:
        print(f"  ✓ {item}")

    print("\nCertifications:")
    for item in profile["certifications"]:
        print(f"  ✓ {item}")

    print("\nProjects:")
    for item in profile["projects"]:
        print(f"  ✓ {item}")

    print("\nLocations:")
    for item in profile["locations"]:
        print(f"  ✓ {item}")

    print("\n" + "=" * 70)
    print("RESUME INTELLIGENCE: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()

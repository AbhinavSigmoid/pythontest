import os
import sys

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.s3_uploader import upload_file

if __name__ == "__main__":
    test_file = "uploads/demo.pdf"
    if not os.path.exists(test_file):
        print(f"Creating dummy file for testing: {test_file}")
        os.makedirs("uploads", exist_ok=True)
        with open(test_file, "w") as f:
            f.write("dummy pdf content")

    print(f"Testing S3 uploader integration using: {test_file}")
    try:
        success = upload_file(test_file)
        if success:
            print("\n>>> S3 UPLOAD INTEGRATION TEST: PASSED SUCCESSFULLY! <<<\n")
        else:
            print("\n>>> S3 UPLOAD INTEGRATION TEST: FAILED. <<<\n")
    except Exception as e:
        print("\n>>> S3 UPLOAD INTEGRATION TEST: FAILED WITH EXCEPTION <<<\n")
        print(e)
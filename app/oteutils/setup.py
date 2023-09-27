from distutils.core import setup, Extension

def main():
	setup(name="oteutils",
		version="1.0.0",
		description="Utils for OTERecorder",
		author="ChasinSpin",
		author_email="test@test.com",
		ext_modules=[Extension("oteutils", ["oteutils/oteutils.c"])])

if __name__ == "__main__":
	main()

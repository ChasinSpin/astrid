from distutils.core import setup, Extension

def main():
	setup(name="ospi",
		version="1.0.0",
		description="OTEStamper SPI Interface",
		author="ChasinSpin",
		author_email="test@test.com",
		ext_modules=[Extension("ospi", ["ospi/ospi.c"])])

if __name__ == "__main__":
	main()

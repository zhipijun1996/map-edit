import inspect,sys
from . import screen_review040_v1 as previous
from .lift_idea_v1 import rows,label

def main():
    source=inspect.getsource(previous.run).replace("'approved-r040-'+row['reviewId']","'approved-lift-'+label(row)")
    namespace={**previous.__dict__,'label':label};exec(compile(source,__file__,'exec'),namespace);namespace['run'](rows()[0],sys.argv[1])
if __name__=='__main__':main()

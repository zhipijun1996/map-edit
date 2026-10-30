import inspect,sys
from . import screen_review040_v1 as previous
from .continue_revision060_v1 import rows,label

def main():
    source=inspect.getsource(previous.run).replace("'approved-r040-'+row['reviewId']","'approved-r060-'+label(row)")
    namespace={**previous.__dict__,'label':label};exec(compile(source,__file__,'exec'),namespace)
    for row in rows():
        if not sys.argv[2:]or label(row)in sys.argv[2:]:namespace['run'](row,sys.argv[1])
if __name__=='__main__':main()

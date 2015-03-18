#include "generated.c"


int main (int argc, const char* argv[])
{
	long* in = (long*) malloc(sizeof(long) * 1024*1024*1024);
	long* out = (long*) malloc(sizeof(long) * 1024 * 1024 * 1024);
	apply(in, out);
	free(in);
	free(out);
}

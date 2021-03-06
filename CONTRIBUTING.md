How to contribute to CFEngine
=============================

Thanks for considering contributing to CFEngine! We take pull-requests
[on GitHub](https://github.com/cfengine/core/pulls) and we have a public
[bug-tracker](https://tracker.mender.io/projects/CFE/issues/). Discussion is taking place
on the [dev-cfengine](https://groups.google.com/forum/#!forum/dev-cfengine)
and [help-cfengine](https://groups.google.com/forum/#!forum/help-cfengine)
mailing lists. You'll find us chatting on Freenode's IRC channels
[#cfengine](https://webchat.freenode.net/?channels=cfengine&nick=) and
[#cfengine-dev](https://webchat.freenode.net/?channels=cfengine-dev&nick=).

Normally, bug fixes have a higher chance of getting accepted than new
features, but we certainly welcome feature contributions. If you have an idea
for a new feature, it might be a good idea to open up a feature ticket in
our [bug-tracker](https://tracker.mender.io/projects/CFE/issues/) and send a
message to dev-cfengine mailing list, before actually contributing the code,
in order to get discussion going.

Merged features and larger changes will be released in the first minor release
(i.e. x.y.0). Please note that such pull requests should be ready for merging
(i.e. adjusted for any feedback) at least two months before
[the scheduled release date](https://cfengine.com/product/supported-versions/)
in order to make it to the first minor release.


Pull Requests
-------------------------------------------------

### Checklist

When submitting your pull request, please make sure you:

* Follow our [Coding Style](#coding-style).

* Address only one issue/feature.
  Smaller pull requests are generally better.

* Add tests.
  C functions should have unit tests.
  Promise types, attributes, and functions should have acceptance tests.

* Pay attention to review comments and CI results.
  We have code analysis and tests which run when you submit your PR.
  You may have to make some changes.

* Check that you don't have any merge conflicts.
  (Rebase on master or target branch).

* Tidy up the commit log by squashing commits.
  Each commit should be a valid change and make sense on its own.
  Usually a Pull Request will only have one commit.

* Add a [ChangeLog Entry](#changelog-entries) to the commit.

* Add a configure option if appropriate:
  `./configure --disable-big-feature` or `./configure --without-libfoo`.


### Multi-repo pull requests

CFEngine is built from several different repositories.
Sometimes a change is needed in multiple repositories.
When possible, try to make changes compatible with the master version of the other repositories.
While our Jenkins Pipeline can handle multiple Pull Requests, Travis does not.
If you are making a breaking change in one repository which has to be merged together with another pull request, make this very clear.
Put this in the pull request description (first comment);

```
Merge together:
cfengine/core#1234
cfengine/buildscripts#333
```

If the change is needed for a bigger feature, make that feature a separate pull request.
The bigger PR will likely take some time to get reviewed, and discussed, while smaller changes can be merged quickly.


Coding Style
------------

Our coding style is loosely based on Allman-4 and the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html).
Keep in mind that these are guidelines, there will always be some situations where exceptions are appropriate.

### Formatting / Whitespace

* Feel free to use `clang-format` to format new code you submit.
  (Our configuration is in `.clang-format`).
* 4 spaces per indentation, no tabs.
* Fold new code at 78 columns.
    * Do not break string literals.
      Prefer having strings on a single line, in order to improve search-ability(grep).
      If they do not fit on a single line, try breaking on punctuation.
      You can surpass the 78 column limit if necessary.
* Use single spaces around operators, but not before semicolon:
  ```c
  int a = 2 + 3;
  int b = 2 * (a - 2);
  if (a > b)
  ```
* Place pointer star to the right, next to the name it belongs to:
  ```c
  int *a;
  char *b, *c;
  const char *const d;
  ```
* Curly brackets on separate lines.
    * Except in a do-while loop, to avoid confusion with a while loop:
      ```c
      do
      {
          // ...
      } while (condition);
      ```
    * Except at the end of a struct type definition:
      ```c
      typedef struct _Name
      {
          // ...
      } Name;
      ```
* Type casts should be separated with one space from the variable:
  ```c
  (struct sockaddr *) &myaddr
  ```

### Readability / Maintainability

Keep in mind that code should be readable by non C experts.
If you are a Guru, try to restrain yourself, only do magic when absolutely necessary.

* Avoid code duplication.
  Make a variable or a function instead of copy-pasting the same patterns.
    * Helper functions which are only used in the same file should be declared `static`.
    * If you want to test the `static` functions, you can `#include` the `.c` file in the unit test.
* Avoid abbreviations.
* Welcome to "modern" C (C99).
    * Declare variables where they are needed, not at the beginning of a function / block.
    * Declare index inside for loop:
      ```c
      for (int i = 0; i < n; ++i)
      ```
* Variable names:
    * Describe what the variable is.
    * Are English words with underscores: `string_index`
    * Boolean variable names should make an `if`/`while` sensible: `if (more_data)` / `while (more_data)`
* Function names:
    * Are `CamelCase` (with first letter capital).
    * Describe what the function does.
* Namespaces:
    * Don't exist in C.
    * But we can pretend, using underscores in function names:
        * `StrList_BinarySearch()`
* Structs:
    * Names are `CamelCase` (with first letter capital).
    * Use the common typedef pattern:
      ```c
      typedef struct _Point
      {
          float x;
          float y;
      } Point;
      ```
      Don't add a trailing `_t` or similar for typedefs.
    * Structs and functions which modify them are similar to classes and methods in other languages.
        * Method names should start with the struct name.
        * The first parameter should be the "self" pointer:
          ```c
          void SeqAppend(Seq *seq, void *item);
          ```
* Document using Doxygen (within reason), preferably in the `.c` files, not the header files.


### Safety / Correctness

* Minimize use of global variables.
* Use pure functions when possible:
    * Functions with no / few side effects are easier to reuse.
    * Use `const` parameters to show that they are not altered.
* Functions which expect their arguments to be non-NULL should assert this at the top:
  ```c
  size_t SeqLength(const Seq *seq)
  {
      assert(seq != NULL);
      return seq->length;
  }
  ```
    * Not necessary all the time, avoid duplication.
      A wrapper like this doesn't need the asserts:
      ```c
      bool SaveXmlDocAsFile(xmlDocPtr doc, const char *file, const Attributes *a, NewLineMode new_line_mode)
      {
          return SaveAsFile(&SaveXmlCallback, doc, file, a, new_line_mode);
      }
      ```
      It's more appropriate to put the asserts close to the code which dereferences the pointers.
* Constants
    * Constify what can be `const`.
    * A pointer to an immutable string:
    ```c
    const char *string;
    ```
    * An immutable pointer to a mutable string:
    ```c
    char *const string;
    ```
    * An immutable pointer to an immutable string:
    ```c
    const char *const string;
    ```
    * The `const` keyword applies to the left, unless it is the first, then it applies to the right.
* Types:
    * Assign and compare using the correct "type" literal:
      ```c
      float temperature = 0.0;
      int dollars = 10;
      char string_terminator = '\0';
      char *name = NULL;
      if (name == NULL && dollars <= 0 && temperature <= -10.0)
      {
          // :(
      }
      ```
* Conditions:
    * Use explicit comparisons:
    ```c
    if (data != NULL)
    ```
    * Have the literal (constant) to the right side, so it reads well:
    ```c
    if (age >= 33)
    ```
    * **NEVER** compare to `true`: ~~`if (data == true)`~~ (`true` is `1`)
    * Don't include assignments inside if/while expressions.
      Put it on the line before.
        * *Unless they avoid great repetition*.
* Error handling:
    * Functions which can fail should return error code (int) or success/failure (bool).
        * Compiler can enforce checking of return value, output of function can be in an output parameter (pointer).
        * Functions which have valid positive return values can use negative numbers for errors.
    * `true`(`bool`) and `0`(`int`) should signify success.
    * Only return an error code (`int`) when there are multiple different return values for different errors. If a function can only return `0` (success) or `-1` (error) use `bool` instead.
* `Destroy` functions should accept NULL pointers (similar to `free()`).
* Don't use `static` variables that change, since they are not thread-safe.
* Sizes of stack-allocated buffers should be deduced using `sizeof()`.
  Never hard-code the size (like `CF_BUFSIZE`).
* Avoid using type casts, unless absolutely necessary.
    * Usually a compiler warning is better satisfied with correct code rather than using a type cast.
* Don't initialize variables unless they need an initial value.
  Unnecessary initialization silences important compiler warnings.

#### String formatting

| Type            | Format string  |
| :-------------- | :------------- |
| `char *`        | `%s`           |
| `int`           | `%d`           |
| `unsigned int`  | `%du`          |
| `long`          | `%l`           |
| `unsigned long` | `%lu`          |
| `size_t`        | `%zu`          |
| `ssize_t`       | `%zd`          |
| `intmax_t`      | `%jd`          |
| `uintmax_t`     | `%ju`          |

See `man 3 printf` for a more complete table.
For other integer types without a format, cast `signed` types to `intmax_t` and `unsigned` types to `uintmax_t`.


Logging Conventions
-----------------------------------

CFEngine outputs messages about what its doing using the `Log()` function. It
takes a `LogLevel` enum mapping closely to syslog priorities. Please try to do
the following when writing output messages.

### Log levels

* `LOG_LEVEL_CRIT`: For critical errors, where process cannot / should not
  continue running, exit immediately.
* `LOG_LEVEL_ERR`: Promise failed or other errors that are definitely
considered bad / not normal.
* `LOG_LEVEL_WARNING`: Something unusual happened that the user should
  investigate. Should be severe enough to warrant investigating further,
  but not as severe as a definitive error/bug.
* `LOG_LEVEL_NOTICE`: Important information (not errors) that must not
be missed by the user. For example cf-agent uses it in files promises
when change tracking is enabled and the file changes.
* `LOG_LEVEL_INFO`: Useful high level information about what the process is
  doing. Examples:
  * Changes performed to the system, for example when a promise has been
    repaired.
  * Server denies access to client based on `access_rules`.
* `LOG_LEVEL_VERBOSE`: Log *human readable* progress info useful to
users (i.e. sysadmins). Also errors that are unimportant or expected
in certain cases.
* `LOG_LEVEL_DEBUG`: Log anything else (for example various progress info).
Try to avoid "Entering function Foo()", but rather use for
"While copying, got reply '%s' from server".

Please keep in mind that some components like `cf-serverd` handle very large
sets of data / connections and logs can become spammy. In some cases
it might be appropriate to create error / warning summaries instead of
outputting a log message every time an event occurs.

### Logging Guidelines

* Do not decorate with symbols or indentation in messages and do not
  terminate the message with punctuation. Let `Log()` enforce the common
  formatting rules.

* When quoting strings, use single quotes, e.g. "Some stuff '%s' happened in
  '%s'.

* Keep in mind context, e.g. write "While copying, insufficient permissions"
  rather than "Insufficient permissions".

* Use output sparingly, and use levels appropriately. Verbose logging tends to
  get very verbose.

* Use platform-independent `GetErrorStr()` for `strerror(errno)`.  Write
  for example
  `Log(LOG_LEVEL_ERR, "Failed to open ... (fopen: %s)", GetErrorStr());`

* Normally, try to keep each message to one line of output, produced
  by one call to `Log()`.

* Normally, do not circumvent `Log()` by writing to stdout or stderr.


Code Overview
-------------

The CFEngine codebase can be usefully thought of as a few separate components:
utilities (libutils), parsing (libpromises), evaluation (libpromises),
actuation (mostly in cf-agent), network (libcfnet).

Over the past year, the structure of the codebase has undergone some
change. The goal of the restructuring is to isolate separate components with
explicit dependencies, and provide better unit test coverage.

For a general introduction to the tools, please read the man pages/documentation.

### libcompat

These are replacement functions in cases where autoconf cannot find a function
it expected to find on the platform. CFEngine takes an approach of relying on
the platform (typically POSIX) as much as possible, rather than creating its
own system abstraction layer.

### libutils

Contains generally useful datastructures or utilities. The key point about
*libutils* is that it is free of dependencies (except *libcompat*), so it does
not know about any CFEngine structures or global state found in *libpromises*.
Some examples of often used files (not meant to be an exhaustive list):

- *sequence.h*: Collection of ordered elements
  (Loosely based on glib GSequence).
- *map.h*: General purpose map (hash table).
- *set.h*: General purpose set, a wrapper of *Map*.
- *writer.h*: Stream writer abstraction over strings and FILEs.
- *string_lib.h*: General purpose string utilities.
- *logging.h*: Log functions, use Log() instead of printf.
- *ip_address.h*: IP address parsing.
- *file_lib.h*: General purpose file utilities.
- *misc_lib.h*: Really general utilities.

### libcfnet

Contains the networking layer for CFEngine. (At the time of writing, a bit of
a moving target). All of this was in libpromises previously. Ideally it would
be completely separate, without depending on libpromises, but we're not there
yet.

### libpromises

This is the remainder of the old src directory, that which has not been
categorized. The roadmap for the project remains to leave *libpromises* as a
component for evaluation.

- *cf3.defs.h*: Contains structure definitions used widely.
- *generic_agent.h*: Common code for all agent binaries.
- *parser.h*: Parse a policy file.
- *syntax.h*: Syntax utilities and type checking.
- *mod_???.c*: Syntax definitions for all promise types (actuation modules).
- *eval_context.h*: Header for EvalContext, keeper of evaluation state.
- *expand.c*: Evaluates promises.
- *policy.h*: Policy document object model, essentially the AST output of the
  parsing stage.
- *evalfunction.c*: Where all the built-in functions are implemented.
- *locks.h*: Manages various persistent locks, kept in a local database.
- *sysinfo.c*: Detects hard classes from the environment (OS, IP, etc.)

Things which should be moved out of *libpromises*:
- *crypto.h*: Crypto utilities for some reason still tied to evaluation state.
- *files_???*: File utilities we haven't been able to decouple from evaluation.

Things you should not use in *libpromises*

- *cf3.extern.h*: Remaining global variables.
- *prototypes3.h*: The original singular header file.
- *item_lib.h*: Item is a special purpose list that has been abused for
  unintended purposes.
- *assoc.h*: An lval-rval pair, deprecated in favor of *EvalContext*
  symbol table.
- *scope.h*: Old symbol table, this will move into *EvalContext*.

### cf-agent

See the documentation for an introduction to cf-agent and the other components.
Since cf-agent is (arguably) the most important component here is a more
technical description of how it works, both during first time setup (bootstrap)
and regular operation. Note that most of the binaries evaluate policy so there
are many similarities to cf-agent.

#### Lifecycle of cf-agent

The following outlines the normal execution of a *cf-agent* run.

1. Read options and gather these in GenericAgentConfig.
2. Create an EvalContext and call GenericAgentConfigApply(ctx, config).
3. Discover environment and set hard classes, apply to EvalContext.
4. Parse input policy file, get a Policy object.
5. Run static checks on Policy object.
6. Evaluate each *Bundle* in *bundlesequence*.
7. Write reports to disk.


#### Bootstrapping cf-agent

The following outlines the steps taken by agent during a successful bootstrap
to a policy server.

1. Remove all files in `inputs` directory
2. Write built-in `inputs/failsafe.cf`
3. Write policy server address or hostname, as was the argument
   to `--bootstrap` option, to `policy_server.dat`.
4. If the host was bootstrapped to the machine's own IP address, then it
   is a policy server, and the file `state/am_policy_hub` is touched as
   marker.
5. cf-agent runs using `failsafe.cf` as input file:
    1. Runs `cf-key` to generate `localhost.{priv,pub}` keys inside
    `ppkeys` directory.
    2. Fetches policy files from the policy server.
    3. Starts `cf-execd`
    4. Runs `cf-agent -f update.cf`
6. Agent finishes.
7. `cf-execd` continues to run `cf-agent` periodically with policy
   from `inputs` directory.


ChangeLog Entries
-----------------

When a new feature or a bugfix is being merged, it is often necessary to be
accompanied by a proper entry in the ChangeLog file. Besides manually editing
the file, we have an automatic way of generating them before the release,
by properly formatting *commit messages*
(see [git-commit-template](misc/githooks/git-commit-template)). Keep in mind
that changelog entries should be written in a way that is understandable by non-
programmers. This means that references to implementation details are not
appropriate, leave this for the non-changelog part of the commit message. It is
the behavior change which is important. This implies that refactorings that have
no visible effect on behavior don't need a changelog entry.

If a changelog entry is needed, your pull request should have at least one
commit either with a "Changelog:" line in it (anywhere after the title), or
title should start with ticket number from our bug tracker ("CFE-1234").
"Changelog:" line may be one of the following:

* To write arbitrary message in the ChangeLog:
`Changelog: <message>`
* To use the commit title line in the ChangeLog:
`Changelog: Title`
* To use the entire commit message in the ChangeLog:
`Changelog: Commit`

It's worth noting that we strive to have bugtracker tickets for most
changes, and they should be mentioned in the ChangeLog entries. In fact
if anywhere in the commit message the string ```CFE-1234``` is found
(referring to a ticket from https://tracker.mender.io ), it will be
automatically added to the ChangeLog.


Testing
-------

It is extremely important to have automated tests for all code, and normally
all new code should be covered by tests, though sometimes it can be hard to
mock up the environment.

There are two types of tests in CFEngine. *Unit tests* are generally
preferable to *acceptance tests* because they are more targeted and take less
time to run. Most tests can be run using `make check`.
See [Unsafe Tests](#unsafe-tests) below.

* *Unit tests*. Unit tests are a great way of testing some new module (header
  file). Ideally, the new functionality is written so that the environment can
  be easily injected and results readily verified.

* *Acceptance tests*. These are tests that run *cf-agent* on a policy file
  that contains *test* and *check* bundles, i.e. it uses CFEngine to both make
  a change and check it. See also script tests/acceptance/testall.

Tip: In order to trigger assert() calls in the code, build with
`--enable-debug` (passed to either `./autogen.sh` or `./configure`). If you get
very large binary sizes you can also pass `CFLAGS='-g -O0'` to reduce that.

Code Coverage
-------------
We strive to always increase code coverage. If you wish to generate code
coverage information then you must autogen or configure with --enable-debug
and --enable-coverage as well as ensure lcov is installed (typically an lcov
package is available in a distribution).
We use gcov to instrument and process coverage information. .gcno files are
generated at compile-time and will not be regenerated if the source code
does not change. So be careful about cleaning those files. .gcda files are
like index files which can be used to generate the .gcov files which lcov
uses to generate lcov.info and the HTML report in the coverage-html directory.
Many IDEs and editors expect a <root>/coverage/lcov.info summary of coverage
information. After running `make check` you can run `make coverage` and
generate this lcov.info summary for use with other tools. If you wish to only
run a few tests which will add to coverage data you can update lcov.info with
`make collect-coverage` which will only collect coverage data, not compile or
run any tests.

For the atom editor, install the package atom-lcov-info.


Unsafe Tests
------------

Note that some acceptance tests are considered to be unsafe because they
modify the system they are running on. One example is the tests for the
"users" promise type, which does real manipulation of the user database on the
system.  Due to their potential to do damage to the host system, these tests
are not run unless explicitly asked for.  Normally, this is something you
would want to do in a VM, so you can restore the OS to a pristine state
afterwards.

To run all tests, including the unsafe ones, you either need to be logged in as
root or have "sudo" configured to not ask for a password. Then run the
following:

    $ UNSAFE_TESTS=1 GAINROOT=sudo make check

Again: DO NOT do this on your main computer! Always use a test machine,
preferable in a VM.


C Platform Macros
-----------------

It's important to have portability in a consistent way. In general we
use *autoconf* to test for features (like system headers, defines,
specific functions). So try to use the autoconf macros `HAVE_DECL_X`,
`HAVE_STRUCT_Y`, `HAVE_MYFUNCTION` etc.  See the
[autoconf manual existing tests section](https://www.gnu.org/software/autoconf/manual/html_node/Existing-Tests.html).

It is preferable to write feature-specific ifdefs, instead of
OS-specific, but it's not always easy. If necessary use these
platform-specific macros in C code:

* Any Windows system: Use `_WIN32`.  Don't use `NT`.
* mingw-based Win32 build: Use `__MINGW32__`.  Don't use `MINGW`.
* Cygwin-based Win32 build: Use `__CYGWIN__`.  Don't use `CFCYG`.
* OS X: Use `__APPLE__`.  Don't use `DARWIN`.
* FreeBSD: Use `__FreeBSD__`.  Don't use `FREEBSD`.
* NetBSD: Use `__NetBSD__`.  Don't use `NETBSD`.
* OpenBSD: Use `__OpenBSD__`.  Don't use `OPENBSD`.
* AIX: Use `_AIX`.  Don't use `AIX`.
* Solaris: Use `__sun`. Don't use `SOLARIS`.
* Linux: Use `__linux__`.  Don't use `LINUX`.
* HP/UX: Use `__hpux` (two underscores!).  Don't use `hpux`.

Finally, it's best to avoid polluting the code logic with many ifdefs.
Try restricting ifdefs in the header files, or in the beginning of
the C files.


Emacs users
-----------

There is Elisp snippet in contrib/cfengine-code-style.el which defines the
project's coding style. Please use it when working with source code. The
easiest way to do so is to add

    (add-to-list 'load-path "<core checkout directory>/contrib")
    (require 'cfengine-code-style)

and run

    ln -s contrib/dir-locals.el .dir-locals.el

in the top directory of the source code checkout.

atexit() and Windows
--------------------

On Windows the atexit function works but the functions registered there are
executed after or concurrently with DLL unloading. If registered functions
rely on DLLs such as pthreads to do locking/unlocking deadlock scenarios can
occur when exit is called.

In order to make behavior more explicit and predictable we migrated to always
using a homegrown atexit system. RegisterCleanupFunction instead of atexit and
DoCleanupAndExit instead of exit.

If `_Exit` or `_exit` need to be called that is fine as they don't call atexit or
cleanup functions.

In some cases such as when exiting a forked process or in executables which don't
register cleanup functions, exit() may be used but a comment should be added
noting that this issue was considered.

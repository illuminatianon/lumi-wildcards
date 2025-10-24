# dynamicprompt wildcard files

## Location:

All wildcards are in the wildcards directory, and each subdir is treated as a namespace. For our current work, we will only be working out of the std/xl namespace.

## Syntax:

  __std/xl/stuff__ - This is a reference to another wildcard file OR a category within a yaml file.
  {a|b|c} - Substitution fragment. Will pick between the three.
  {4$$a|b|c} - Choose 4 from the list. Can use references as well, e.g. {4$$__std/xl/stuff__}
  {4$$, $$__std/xl/stuff__} - Choose 4 from the list and concatenate with a comma.


## Formats:

There are two formats:

1. a list of options, each on a new line
1. a yaml file with a list of options under a key

YAML has some special restrictions:

 - First key must be the filename,
   e.g., filename=std/xl/stuff, then the first key will be stuff:
 - All under the first one.
 - Any line which begins with special character such as { must be qouted. Other entries do not.

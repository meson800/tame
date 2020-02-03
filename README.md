# tame
An unobtrusive YAML based metadata system for arbitrary data management.

## Rationale
In many fields, large amounts of interlinked data are generated. Contextual information, such as the experimental layout of the plate used for microscopy or the configuration of a system used to generate a large profile file, is sometimes stored in the relevant file formats. However, the more common case is that this contextual information must be encoded elsewhere.

`tame` aims to be a minimal metadata management system. Metadata is written in the form of YAML files, without defined schemas. These metadata files should always remain human-understandable, even if generated by external tools. In the case of scientific data, these metadata files must often be written by the scientist, which means that complicated non-plaintext formats or even heavily-delimited plain-text formats (ala JSON) are untenable. At the same time, having this metadata be computer-readable is a boon; relations between files can be programmatically queried, used, and modified.

## Basic use
#### Writing metadata files
For each piece data you want to attach metadata to, write a YAML document. `tame` only looks for one required tag for each metadata file, a `type` key. Normally, the `files` key is also present, unless there is a piece of data that is metadata-only. Optionally, the keys `name` and `uid` can be included and have a special meaning for `tame`. Other keys may be present and remain tracked by `tame`.

 - `type`: A use-specific term describing what information is being tracked. User-written custom code, such as validators or locators, primarily operates on different types.
 - `files` _(required, unless you have a metadata-only document)_: Which files the metadata is attached to. Paths to files can either be *absolute* or *relative to the location of the YAML document*.
 - `name` _(optional)_: A string describing what the metadata describes. In the absence of a `uid` field, the name and type of metadata is used for linking pieces of metadata together. `tame` allows multiple pieces of metadata to have the same type and name.
 - `uid` _(optional)_: A string referring to a piece of metadata. `tame` enforces that two pieces of metadata _cannot_ have the same `uid` and `type`. When the `uid` is present, it can be used for linking metadata together.
 

#### Linking metadata together
Most metadata is not entirely self-contained, and needs contextual information. `tame` handles this with _parent links_. A piece of metadata can be linked to any number of other metadata entries. These links can be specified in one of three ways:
- By filename. A single key is expected in this case, with value `file`. This directly links a piece of metadata to the named YAML document.
- By type/name. Two key/value pairs are expected. This attempts to link this piece of metadata to another piece of metadata, looked up by type/name. This can fail if there are multiple pieces of metadata with the same type and name!
- By type/uid. Because `meta` enforces that type/uid's are unique, there cannot be multiple pieces of metadata with the same type and UID.
- TODO: locators. How to link to "submetadata" files.

See the example below for more details.

Links are specified with a YAML list from the key `parent`.

#### Example
Imagine a directory layout as follows:
```
├──plasmids
│   ├───GFP.gb
│   └───GFP.yaml
├──microscopy
│   ├───20200101.yaml
│   ├───green_channel.tif
│   ├───red_channel.tif
│   └───overlay.tif

```
with a plasmid YAML file: 

`plasmids/GFP.yaml`
```
---
type: plasmid   # Required meta tag
name: GFP       # Optional tag for linking purposes
uid: p001       # Optional tag for linking purposes
files:          # Required meta tag
  - GFP.gb      # This file is specified using a relative path
resistance: Amp # Use-specific tag (in this case a biology metadata field)
```

If the microscopy experiment needs to be linked to the plasmid,
we could specify the linkage in one of these three ways: 

`microscopy/20200101.yaml`
```
---
type: image
files:
  - green_channel.tif
  - red_channel.tif
  - overlay.tif
parent:
  - file: ../plasmids/GFP.yaml # Directly specify the parent relationship
  - type: plasmid              # Specify the parent relationship with
    name: GFP                  # a type/name pair, using explicit YAML syntax
  - {type: plasmid, uid: p001} # Specify the parent relationship with inline YAML syntax
```

## Software support
`tame` supports four basic operations that act on these linked metadata trees, `validate`, `describe`, `collect`, and `freeze`. 
#### `tame validate`
When given a single file, `tame validate` verifies that the given YAML document is in fact valid YAML. If it is, `tame` then verifies that the entire tree of parent relationships is valid. `tame` raises an error if there is invalid YAML syntax somewhere, if a parent link cannot be found, or if there is a type/name collision given a parent link.

When given a directory, `tame` performs this validation operation on all reachable YAML files beneath the directory.

TODO: How do we ensure that a project that has non-meta YAML files is covered/doesn't error out when we do this? Should we switch the filetype to ".meta" instead of just ".yaml"? That would break the idea that you could use this metadata system even without the program `tame`

#### `tame describe`
Given a YAML data file, this attempts to "describe" the metadata item, often by giving information derived from itself and its parents. This is often extended by user code to give meaningful information to all of the other key:value pairs that `tame` does not normally care about.

#### `tame collect`
Given a metadata file, this tells `tame` to collect tne entire tree of parent links from the given metadata file into a self-contained directory. This collection then has the complete contextual information to be shared elsewhere. In the micrscopy example above, performing a `tame collect` on the GFP.yaml file would only include itself and the GFP plasmid, because this plasmid does not depend on anything else. Performing a `tame collect` on the microscopy YAML file would include both the micrscopy images _and_ the GFP plasmid file, because the parental link means that the image should not be separated from its context of the plasmid from which the cells came from.

#### `tame freeze`
TODO: finish thinking about what this means. The goal is to have a command that would:
- Expand wildcards into the specifically included files (e.g. if someone wrote *.tif, it actually "freezes" the file include to whatever TIF files are currently present.
- Hash the included files, saving the hash value, to make sure we have confirmation that files have not been modified.

This moves uncomfortably towards a version control system. If you freeze, you should probably save the frozen original files somewhere, as there's no other way to make sure they don't get modified.

## Finding metadata files
TODO: decide how to do this. Could use a root system, e.g. a tame.yaml file at the top-level, where subdirectories are searched from that point downward.

## Extending `tame` to your metadata scheme
For most usecases, no Python has to be written to extend `tame`. Just start writing YAML files!

`tame` is extended with Python in two important ways, via `locators` and `descriptors`. At the top-level of the tracked metadata, the user can write Python code that implements this locator and descriptor for each `type` of metadata.

#### Locators
Locators allow an additional level of granualartiy in parent links. As an example on where this might be useful, consider a multiple-sample experiment. One metadata YAML file might describe the relevant information of the entire experiment, but there may be additional pieces of data such as micrscopy images that only pertain to single samples. Locators are then the logic that links/matches metadata files together at this sub-file level.

TODO: extend with examples/more reasoning

#### Descriptors
Descriptors are given a Python view of a metadata file of a given type, and are responbible for formatting the output of a `tame describe` call. The default descriptor simply prints out the key/value pairs that are not special/reserved for `tame`.

TODO: extend with examples/more reasoning

## Development setup
This project uses a development strategy inspired by [git-flow](https://nvie.com/posts/a-successful-git-branching-model/). For release sanity and simplicity of non-developers cloning the repository, the `master` branch is _always_ a stable release. Main development occurs on the `develop` branch, so switch to that branch if you want to make changes!

Feel free to ignore the git-flow-ism's of unnecessary merge commits.

## License
This software is released under the [MIT license](LICENSE). This code should be as free as your metadata.

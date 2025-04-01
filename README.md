# release-notes-writer
Compile release notes as a Markdown table from PR titles and descriptions

This is pre-alpha software: in effect, it's just a utility script to decrease
slightly the amount of manual work needed to publish KoboToolbox release
notes at https://community.kobotoolbox.org/tags/c/announcements/7/release-notes

# create-gh-releases

Create a GitHub release for the following KoboToolbox repositories:

- [kobo-docker](https://github.com/kobotoolbox/kobo-docker/releases)
- [kobo-install](https://github.com/kobotoolbox/kobo-install/releases)
- [KPI](https://github.com/kobotoolbox/kpi/releases)

### Usage: 

```
➜  release-notes-writer git:(main) ✗ source ./env
➜  release-notes-writer git:(main) ✗ python3 create-gh-releases.py <tag> <link.to.release.notes>
```

**Example:**

```
python3 create-gh-releases.py 2.099.01 https://community.kobotoolbox.org/t/release-2-099-01/111111/1
```


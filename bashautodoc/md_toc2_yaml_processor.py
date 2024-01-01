import logging
import sys
from collections import defaultdict

from rich import print as rprint

from bashautodoc.helpo import hfile, hstrops
from bashautodoc.regex_patterns import *

LOG = logging.getLogger(__name__)

# TODO: initialise all regex patterns in a single place


# TODO: refactor the hell out of this ;o)
# TODO: sort out conversion of relative paths sooner
class MdToc2YamlProcessor:
    def __init__(self, conf, hwdocs_infiles, search_path) -> None:
        ### For every mdfile
        # 1. establish if it has a TOC
        # 2. Map the hierarchy of nav-doc links via the TOC
        # 3. We will use the anchor "## Table of Contents" to find md TOC

        self.project_docs_dir = conf.get("project_docs_dir") + "/"
        LOG.debug("project_docs_dir: %s", self.project_docs_dir)
        # sys.exit(42)
        #
        self.toc_dict = {}
        self.hierarchy_dict = defaultdict(list)
        self.final_dict = {}

        self.hwdocs_infiles = hwdocs_infiles
        rprint("hwdocs_infiles", self.hwdocs_infiles)
        # sys.exit(42)

        self.mdtoc_path_list = hfile.flatten_list(
            nested_list=hfile.find_files_with_grep_patt(
                search_path=search_path,
                file_glob="*.md",
                txt_pattern="## Table of Contents",
            )
        )
        rprint("mdtoc_path_list", self.mdtoc_path_list)
        # sys.exit(42)

    @staticmethod
    def clean_mdtoc_list(toc_mdlist):
        clean_toc_mdlist = []
        for line in toc_mdlist:
            line_stripped = line.strip()
            if "## Table of Contents" in line_stripped:
                pass
            elif line_stripped == "":
                pass
            else:
                mdlink_match = mdlink_patt.search(line_stripped)
                if mdlink_match:
                    mdlink = mdlink_match.group(2)
                    clean_toc_mdlist.append(mdlink)
        return clean_toc_mdlist

    def gen_toc_dict_from_mdindex_files(self):
        for mdpath in self.hwdocs_infiles:
            mdpath_rel = mdpath.replace(self.project_docs_dir, "")
            file_text = hfile.read_file_2string(filepath=mdpath)
            if "## Table of Contents" in file_text:
                table_of_contents = (
                    hstrops.extract_lines_between_start_and_end_blank_line_tag(
                        file_text, start_tag="## Table of Contents"
                    )
                )
                self.toc_dict[mdpath_rel] = MdToc2YamlProcessor.clean_mdtoc_list(
                    toc_mdlist=table_of_contents
                )
            else:
                self.toc_dict[mdpath_rel] = None

        rprint("\ntoc_dict", self.toc_dict)
        sys.exit(42)

    def construct_hierarchy_dict(self):
        for mdpath, _ in self.toc_dict.items():
            rprint("mdpath", mdpath)
            for file_path2, toc_links2 in self.toc_dict.items():
                rprint("file_path2", file_path2)
                mdpath_rel = mdpath.replace(self.project_docs_dir, "")
                if mdpath_rel in toc_links2:
                    self.hierarchy_dict[file_path2].append(mdpath_rel)
                    break
        rprint("\nhierarchy_dict", self.hierarchy_dict)

    def order_indexes_in_toc_dict(self):
        # copy index files to front of list
        # catnames_list = list(self.toc_dict.keys())
        for mdpath, toc_links in self.toc_dict.items():
            rprint("mdpath", mdpath)
            # rprint("toc_links", toc_links)
            # sys.exit(42)
            toc_links_with_index = []
            if mdpath == "docshw/index.md":
                # TODO: fix this hard coded hack - think we need to specify main index in config
                continue
            for mdlink in toc_links:
                if mdpath != mdlink:
                    rprint("mdlink", mdlink)
                    ### deletes the index.mdfile from the list
                    # (as we want to make this the forst element in the list)
                    toc_links_with_index.append(mdlink)
            toc_links_with_index.insert(
                0, mdpath
            )  ### inserts the index.mdfile at the start of the list
            self.toc_dict[mdpath] = toc_links_with_index
        rprint("\ntoc_dict index ordered", self.toc_dict)

    def construct_final_dict(self):
        for key, link_list in sorted(
            self.hierarchy_dict.items(), key=lambda x: len(x[1]), reverse=True
        ):
            rprint("link_list", link_list)

            self.final_dict[key] = self.toc_dict[key]
            # rprint("final_dict", self.final_dict)
            # sys.exit(42)

            new_link_list = []
            for md_link in self.final_dict[key]:
                if md_link in link_list:
                    rprint("md_link", md_link)
                    # sys.exit(42)
                    category_split = md_link.split("/")
                    if category_split[-1] == "index.md":
                        category_name = category_split[-2]
                    else:
                        category_name = category_split[-1]

                    yaml2_sublist = []
                    for link in self.toc_dict[md_link]:
                        yaml2_sublist.append(
                            {
                                link.split("/")[-1].replace(".md", ""): link.replace(
                                    self.project_docs_dir, ""
                                )
                            }
                        )

                    sub_dict = {category_name: yaml2_sublist}
                    new_link_list.append(sub_dict)
                else:
                    # TODO: make category split a function
                    new_link_list.append(
                        {
                            md_link.split("/")[-1].replace(".md", ""): md_link.replace(
                                self.project_docs_dir, ""
                            )
                        }
                    )
            self.final_dict[key] = new_link_list
        rprint("final_dict", self.final_dict)

    def main(self):
        self.gen_toc_dict_from_mdindex_files()
        # sys.exit(42)

        ## 1. Check which mdtoc_path is in which list to figure out rough order
        ## 2. If it is in the list, then it is suboridnate
        ## 3. Create ranked order of mdfiles
        self.construct_hierarchy_dict()
        sys.exit(42)

        self.order_indexes_in_toc_dict()
        # sys.exit(42)

        self.construct_final_dict()
        sys.exit(42)

        return self.final_dict

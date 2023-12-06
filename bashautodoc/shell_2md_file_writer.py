"""
This module contains the Sh2MdFileWriter class which is responsible for
converting shell source files to markdown files for documentation.

The Sh2MdFileWriter class takes in configuration information, function text
and dependency dictionaries, a list of full alias strings, the source file path,
and the project documentation directory. It organizes markdown files into
subdirectories, processes functions and aliases, and writes out the markdown file.

Example:
    writer = Sh2MdFileWriter(conf="config",
                             cite_about="about citation",
                             func_text_dict={},
                             func_dep_dict={},
                             full_alias_str_list=[],
                             src_file_path="file1",
                             project_docs_dir="docs/")
    writer.main_write_md()
"""
import logging
import sys

from mdutils.mdutils import MdUtils

from bashautodoc.DocSectionWriterFunction import DocSectionWriterFunction
from bashautodoc.helpo.hfile import mkdir_if_notexists
from bashautodoc.helpo.hstrops import str_multi_replace

LOG = logging.getLogger(__name__)


class Sh2MdFileWriter:
    """Converts shell source files to markdown files for documentation."""

    def __init__(
        self,
        conf,
        cite_about,
        func_text_dict,
        func_dep_dict,
        full_alias_str_list,
        src_file_path,
        project_docs_dir,
    ):
        """
        Initialize the Shell2MdFileWriter.

        Args:
            conf (str): Configuration information.
            cite_about (str): About citation.
            func_text_dict (dict): Dictionary of function names and their code.
            func_dep_dict (dict): Dictionary of function dependencies.
            full_alias_str_list (list): List of full alias strings.
            src_file_path (str): Path to the source file.
            project_docs_dir (str): Directory path for project documentation.

        Example:
            writer = Shell2MdFileWriter(conf="config",
                                        cite_about="about citation",
                                        func_text_dict={},
                                        func_dep_dict={},
                                        full_alias_str_list=[],
                                        src_file_path="file1",
                                        project_docs_dir="docs/")
        """
        self.conf = conf
        self.cite_about = cite_about
        self.func_text_dict = func_text_dict
        self.func_dep_dict = func_dep_dict
        self.full_alias_str_list = full_alias_str_list
        self.src_file_path = src_file_path
        self.project_docs_dir = project_docs_dir

        self.sh2_md_file_writers = [
            "about",
            "group",
            "param",
            "example",
        ]

        # self.cparam_sort_mapper = {
        #     ">***about***": 0,
        #     ">***group***": 1,
        #     ">***param***": 2,
        #     ">***example***": 3,
        # }

        self.main_write_md()

    def write_aliases_section(self):
        """
        Write the aliases section to the markdown file.

        Example:
            writer = Shell2MdFileWriter(conf="config",
                                        cite_about="about citation",
                                        func_text_dict={},
                                        func_dep_dict={},
                                        full_alias_str_list=[],
                                        src_file_path="file1",
                                        project_docs_dir="docs/")
            writer.write_aliases_section()
        """
        self.mdFile.new_header(
            level=2, title="Aliases", style="atx", add_table_of_contents="n"
        )

        mytable = ""
        mytable += "| **Alias Name** | **Code** | **Notes** |\n"
        mytable += "| ------------- | ------------- | ------------- |\n"
        for myalias in self.full_alias_str_list:
            mytable += myalias  # "| **" + ppass + "** | " + pp_dict[stack] + " |\n"

        self.mdFile.new_paragraph(mytable)

    def organise_mdfiles_2subdirs(self):
        """
        Organize markdown files into subdirectories.
        """
        # probably only does one level
        category_names = self.conf.get("category_names")

        infile_path_list = self.src_file_path.split("/")
        LOG.debug("infile_path_list: %s", infile_path_list)

        LOG.debug("shell_glob_patterns: %s", self.conf.get("shell_glob_patterns"))

        outfile_name = str_multi_replace(
            input_str=infile_path_list[-1],
            rm_patt_list=self.conf.get("shell_glob_patterns"),
            replace_str=".md",
        )
        LOG.debug("outfile_name: %s", outfile_name)

        relative_src_path = self.src_file_path.replace(
            self.conf.get("project_docs_dir"), ""
        )
        full_outfile_path = None
        for catname in category_names:
            if f"/{catname}/" in relative_src_path:
                outfile_path = self.project_docs_dir + "/" + catname
                mkdir_if_notexists(target=outfile_path)
                full_outfile_path = outfile_path + "/" + outfile_name
                LOG.debug("full_outfile_path: %s", full_outfile_path)
                # sys.exit(42)

                return full_outfile_path

        udef_path = self.project_docs_dir + "/" + "undef"
        mkdir_if_notexists(target=udef_path)

        return udef_path + "/" + outfile_name

    def main_write_md(self):
        """
        Perform the main routine of writing markdown files.

        This routine organizes markdown files into subdirectories, processes
        functions and aliases, and writes out the markdown file.
        """
        full_outfile_path = self.organise_mdfiles_2subdirs()

        # if "/plugins/" in full_outfile_path:
        #     print("full_outfile_path = ", full_outfile_path)
        #     sys.exit(42)

        self.mdFile = MdUtils(file_name=full_outfile_path, title=self.cite_about)
        relative_md_path = self.src_file_path.replace(
            self.conf.get("project_docs_dir"), ""
        )
        self.mdFile.new_paragraph(f"***(in {relative_md_path})***")

        if "/explain.plugin" in relative_md_path:
            print("func_text_dict = ", self.func_text_dict)
            print("func_dep_dict = ", self.func_dep_dict)

            # sys.exit(42)

        ### Process functions
        if len(self.func_text_dict) > 0:
            doc_section_writer_function = DocSectionWriterFunction(
                mdFile=self.mdFile,
                func_text_dict=self.func_text_dict,
                func_dep_dict=self.func_dep_dict,
                cite_parameters=self.sh2_md_file_writers,
            )
            doc_section_writer_function.write_func_section()

        ### Process aliases
        if len(self.full_alias_str_list) > 0:
            self.write_aliases_section()

        ### Write out .md file
        self.mdFile.create_md_file()

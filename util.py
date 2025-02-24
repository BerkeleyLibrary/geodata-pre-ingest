import workspace_directory


def setup_workspace(parent_path):
     workspace_directory.source_batch_directory_path = fr"{parent_path}\source_batch_directory_path"
     workspace_directory.projected_batch_directory_path = fr"{parent_path}\source_batch_projected"     
     workspace_directory.csv_files_directory_path = fr"{parent_path}\csv_files_directory_path"
     workspace_directory.csv_files_arkid_directory_path = fr"{parent_path}\csv_files_arkid_directory_path"
     workspace_directory.results_directory_path = fr"{parent_path}\results_directory_path"
     workspace_directory.log_directory_path = fr"{parent_path}\log_directory_path"

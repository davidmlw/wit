import os
from lib.manifest import Manifest


def inspect_tree(ws, args):
    tree = {}
    root_packages = ws.manifest.packages
    for package in root_packages:
        ident = _get_package_ident(package)
        tree[ident] = _get_package_tree(package)

    processed_lockfile_packages = {pkg.name: pkg.revision for pkg in ws.lock.packages}
    new_tree = _clean_tree(tree, processed_lockfile_packages)
    _print_pkg_tree(new_tree)


def _get_package_tree(root_pkg):
    manifest_path = root_pkg.get_path()/'wit-manifest.json'
    if not os.path.isfile(str(manifest_path)):
        return {}
    data = {}
    manifest = Manifest.read_manifest(root_pkg.wsroot, manifest_path)
    for package in manifest.packages:
        ident = _get_package_ident(package)
        data[ident] = _get_package_tree(package)
    return data


def _get_package_ident(package):
    return "{}@{}".format(package.name, package.revision)


def _clean_tree(tree, lockfile_package_dict):
    if not tree:
        return {}
    cleaned_tree = {}
    for key in tree:
        pkg_name = key.split("@")[0]
        if pkg_name in lockfile_package_dict:
            old_revision = key.split("@")[1]
            new_revision = lockfile_package_dict[pkg_name]
            if new_revision != old_revision:
                new_key = "{}->{}".format(key, new_revision)
                cleaned_tree[new_key] = {}
                continue
        cleaned_tree[key] = _clean_tree(tree[key], lockfile_package_dict)
    return cleaned_tree


def _print_pkg_tree(data):
    return _recur_print_pkg_tree(0, data, list(data.keys()), 0, [])


def _recur_print_pkg_tree(depth, data, keys, idx, done_cols):
    done_cols_copy = done_cols[:]
    key = keys[idx]
    end = idx == len(keys)-1
    if depth > 0:
        for i in range(1, depth):
            if i in done_cols:
                print("   ", end="")
            else:
                print("│  ", end="")
        if end:
            print("└─ ", end="")
            done_cols_copy.append(depth)
        else:
            print("├─ ", end="")

    print(_format_pkg_key(key))

    if data[key]:
        _recur_print_pkg_tree(depth+1, data[key], list(data[key].keys()), 0, done_cols_copy)
    if not end:
        _recur_print_pkg_tree(depth, data, keys, idx+1, done_cols_copy)


def _format_pkg_key(s):
    name = s.split("@")[0]
    rev = s.split("@")[1]
    out = "{}@".format(name)
    if "->" in s:
        parts = rev.split("->")
        rev_old = parts[0][:8]
        rev_new = parts[1][:8]
        out += "{}->{}".format(rev_old, rev_new)
    else:
        out += "{}".format(rev[:8])
    return out
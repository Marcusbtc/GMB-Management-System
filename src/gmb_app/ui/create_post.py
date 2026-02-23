import streamlit as st

from src.gmb_app.integrations import drive_client, gbp_client
from src.gmb_app.services.post_service import build_post_payload, payload_hash, publish_post

TOPIC_TYPE_OPTIONS = ["STANDARD", "OFFER", "EVENT"]
CTA_TYPES = ["BOOK", "ORDER", "SHOP", "LEARN_MORE", "SIGN_UP", "CALL"]


def render_create_post_tab(credentials, location_id, selected_account_id, t):
    st.header(t("create_post"))

    if not credentials:
        st.info(t("auth_first"))
        return

    if location_id == "location_id_placeholder":
        st.info(t("select_location_first"))
        return

    defaults = {
        "create_post_image_source": "none",
        "create_post_image_url_input": "",
        "create_post_image_url": "",
        "drive_current_folder_id": "root",
        "drive_folder_stack": [],
        "drive_selected_folder_id": "root",
        "create_post_prev_source": "none",
        "create_post_busy": False,
        "create_post_last_payload_hash": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    image_options = ["none", "url", "drive"]
    topic_type = st.selectbox(t("post_type"), TOPIC_TYPE_OPTIONS, index=0, key="create_post_topic_type")
    language_code = st.text_input(t("language_code"), value="pt-BR", key="create_post_language_code")
    summary = st.text_area(t("post_text"), height=180, placeholder="Write your post content...", key="create_post_summary")
    st.caption(f"{t('characters')}: {len(summary.strip())}")

    include_cta = st.checkbox(t("include_cta"), key="create_post_include_cta")
    cta_type, cta_url = None, None
    if include_cta:
        cta_type = st.selectbox(t("cta_type"), CTA_TYPES, key="create_post_cta_type")
        cta_url = st.text_input(t("cta_url"), placeholder="https://example.com", key="create_post_cta_url")

    image_source = st.radio(
        t("image_source"),
        options=image_options,
        horizontal=True,
        format_func=lambda opt: {"none": t("image_none"), "url": t("image_url"), "drive": t("image_upload_drive")}[opt],
        key="create_post_image_source",
    )

    if st.session_state.get("create_post_prev_source") != image_source:
        st.session_state["create_post_image_url_input"] = ""
        st.session_state["create_post_image_url"] = ""
        st.session_state["create_post_prev_source"] = image_source

    image_file = None
    if image_source == "url":
        image_url_input = st.text_input(t("image_url"), placeholder="https://.../image.jpg", key="create_post_image_url_input")
        st.session_state["create_post_image_url"] = image_url_input.strip()
    elif image_source == "drive":
        image_file = st.file_uploader(t("select_image"), type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False, key="create_post_image_file")
        if image_file is not None:
            st.caption(f"{t('file_ready')}: {image_file.name}")

        with st.expander(t("drive_folder_browser"), expanded=False):
            st.caption(f"{t('current_folder')}: `{st.session_state['drive_current_folder_id']}`")
            try:
                folders = drive_client.list_folders(credentials, st.session_state["drive_current_folder_id"])
            except Exception as e:
                st.error(f"{t('drive_upload_failed')}: {e}")
                folders = []

            folder_options = {f["name"]: f["id"] for f in folders}
            selected_folder_name = st.selectbox(t("subfolders"), options=["-"] + list(folder_options.keys()), key="drive_subfolder_select")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(t("open_folder"), key="drive_open_folder_btn") and selected_folder_name != "-":
                    st.session_state["drive_folder_stack"].append(st.session_state["drive_current_folder_id"])
                    st.session_state["drive_current_folder_id"] = folder_options[selected_folder_name]
                    st.rerun()
            with col2:
                if st.button(t("back"), key="drive_back_folder_btn") and st.session_state["drive_folder_stack"]:
                    st.session_state["drive_current_folder_id"] = st.session_state["drive_folder_stack"].pop()
                    st.rerun()
            with col3:
                if st.button(t("use_current_folder"), key="drive_use_current_folder_btn"):
                    st.session_state["drive_selected_folder_id"] = st.session_state["drive_current_folder_id"]

            st.caption(f"{t('selected_folder')}: `{st.session_state.get('drive_selected_folder_id', 'root')}`")

        if st.button(t("upload_to_drive"), key="drive_upload_btn", disabled=st.session_state["create_post_busy"]):
            if image_file is None:
                st.error(t("select_file_before_upload"))
            else:
                try:
                    st.session_state["create_post_busy"] = True
                    progress = st.progress(0)
                    progress.progress(10)
                    uploaded = drive_client.upload_file_to_folder(
                        credentials,
                        st.session_state.get("drive_selected_folder_id", "root"),
                        image_file.name,
                        image_file.getvalue(),
                        image_file.type,
                    )
                    progress.progress(45)
                    drive_client.set_file_public(credentials, uploaded["id"])
                    progress.progress(70)
                    public_url = drive_client.build_public_file_url(uploaded["id"])
                    if not drive_client.validate_public_url(public_url):
                        drive_client.set_file_public(credentials, uploaded["id"])
                        progress.progress(85)
                        if not drive_client.validate_public_url(public_url):
                            raise ValueError(t("url_not_public"))
                    st.session_state["create_post_image_url"] = public_url
                    progress.progress(100)
                    st.success(t("drive_upload_success"))
                except Exception as e:
                    st.error(f"{t('drive_upload_failed')}: {e}")
                finally:
                    st.session_state["create_post_busy"] = False

        if st.session_state.get("create_post_image_url"):
            st.caption(f"{t('public_link_ready')}: {st.session_state['create_post_image_url']}")
    else:
        st.session_state["create_post_image_url_input"] = ""
        st.session_state["create_post_image_url"] = ""

    submitted = st.button(
        t("publishing_in_progress") if st.session_state["create_post_busy"] else t("publishing"),
        key="create_post_publish_btn",
        disabled=st.session_state["create_post_busy"],
    )
    if not submitted:
        return

    try:
        st.session_state["create_post_busy"] = True
        resolved_image_url = ""
        if image_source == "url":
            resolved_image_url = st.session_state.get("create_post_image_url_input", "").strip()
            if not (resolved_image_url.startswith("http://") or resolved_image_url.startswith("https://")):
                st.error(t("img_url_invalid"))
                return
        elif image_source == "drive":
            resolved_image_url = st.session_state.get("create_post_image_url", "").strip()
            if not resolved_image_url:
                st.error(t("prepare_image_first"))
                return

        payload = build_post_payload(
            summary=summary,
            topic_type=topic_type,
            language_code=language_code,
            cta_type=cta_type,
            cta_url=cta_url,
            image_url=resolved_image_url,
        )
        digest = payload_hash(payload)
        if digest == st.session_state.get("create_post_last_payload_hash", ""):
            st.warning(t("already_published"))
            return

        progress = st.progress(0)
        progress.progress(20)
        created = publish_post(credentials, location_id, selected_account_id, payload)
        progress.progress(70)
        gbp_client.invalidate_posts_cache()
        st.session_state["posts"] = gbp_client.get_posts(credentials, location_id, selected_account_id)
        progress.progress(100)
        st.session_state["create_post_last_payload_hash"] = digest
        st.success(f"{t('post_success')}: {created.get('name', 'created')}")
        with st.expander("Created payload"):
            st.json(created)
    except Exception as e:
        st.error(f"{t('post_error')}: {e}")
    finally:
        st.session_state["create_post_busy"] = False

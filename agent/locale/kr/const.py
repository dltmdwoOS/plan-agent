# model.py
PLAN_MODEL_DESC = {
    'plan': (
        "계획의 단계들을 나타내는 딕셔너리 리스트.\n"
        "각 딕셔너리는 'tool' (수행할 행동)과 'message' (추가 메모)를 포함합니다.\n"
        "예시: [{'tool': 'get_datetime', 'message': '오늘 날짜 파악'}, {'tool': 'web_search', 'message': '이전 단계에서 파악한 날짜로, 'x월 x일 서울 날씨'와 같은 query를 통해 오늘 서울의 날씨 검색'}]\n"
    )
}
TOOL_DECISION_MODEL_DESC = {
    'tool': "선택할 tool 이름. 현재 사용 가능한 tool 중 하나여야 합니다.",
    'tool_input': "선택한 tool을 호출할 때 넘겨줄 매개변수 딕셔너리",
    'message': "선택 이유·메모 (선택)"
}
VALIDATION_MODEL_DESC = {
    'is_valid': "계획 및 실행이 유효했는지 여부. True면 계획이 성공적으로 실행되었음을 의미하고, False면 실패했으므로 다시 계획을 짜야함을 의미합니다.",
    'message': "검증 결과에 대한 설명 메시지. 선택 사항으로, 검증 결과에 대한 추가 정보를 제공할 수 있습니다."
}

# graph.py
TOOL_VALIDATOR_MSG = {
    'unexpected_keys'       : "Unexpected keys present: {unexpected_keys}. Allowed keys are {allowed_keys}.",
    'missing_keys'          : "Missing required keys: {missing_keys}.",
    'yaml_path_not_exist'   : "Description file not found for tool: {tool_name}.",
    'yaml_load_error'       : "Failed to load YAML for tool {tool_name}: {e}",
}
SPECIAL_TOOL_MSG = {
    'save_chat_memory'  : "대화 내역을 성공적으로 저장했습니다.",
    'clear_chat_memory' : "대화 내역을 성공적으로 초기화했습니다."
}
CHAT_MSG = {
    'input_message'                 : "Input: {user_input}",
    'attempt_message'               : "\nAttempt {n_recursion}",
    'plan_message'                  : "Plan: {plan}",
    'tool_validation_false_message' : "Step {step} Error : {message}",
    'tool_complete_message'         : "Plan Step {step} Tool: {tool_json}",
    'tool_output_message'           : (
                                        "Plan Step {step} Tool Output:\n"
                                        "<OUTPUT START>\n{tool_output}\n<OUTPUT END>"
                                      ),
    'current_tool_message'          : "Current Step: {tool_json} TODO!",
    'validation_true_message'       : (
                                        "Accepted: True\n"
                                        "Validation Message: {validation_message}"
                                      ),
    'validation_false_message'      : (
                                        "Accepted: False\n"
                                        "Validation Message: {validation_message}\n"
                                        "지금까지 일련의 과정은 통과받지 못했습니다. Validation에 기반해 계획을 다시 세워야 합니다."
                                      ),
    'max_attempt_exceeded_message'  : "최대 Attempt 횟수가 초과되었습니다. 더 이상 Plan 재설정 및 Tool 사용이 불가능합니다."
    
}

# memory.py
MEMORY_CONST = {
    'summary_input': "지금까지의 대화 내역을 요약하세요.",
    'load_error_message': "대화 내역을 불러오는 중 오류가 발생했습니다: {e}",
    'save_error_message': "대화 내역을 저장하는 중 오류가 발생했습니다: {e}",
}

# Tool related
EXECUTE_CODE_CONST = {
    'tabu_import': "❌ 허용되지 않은 모듈/함수를 포함하고 있어 실행이 거부되었습니다.",
    'forbidden_module': "❌ 금지된 모듈 import 발견 → 실행 거부",
    'parsing_failed': "❌ 코드 파싱 실패",
    'timeout': "⏰ 실행 시간이 제한({timeout} 초)을 초과했습니다.",
    'no_output': "✅ 실행 완료 (출력 없음)",
    'desc': """
    로컬 Python 환경에서 입력한 코드를 실행합니다.  
    간단한 테스트나 ‘빠른 코드 스니펫 검증’이 필요할 때 유용합니다.
    (※ 프로덕션용이 아니며, 보안 격리가 제한적입니다.)

    Args:
        code (str): 실행할 Python 코드 문자열. `print` 등의 출력 함수를 한 번도 사용하지 않는다면 그 어떤 것도 출력 및 반환하지 않습니다.
                    예) "for i in range(3): print(i)"
        timeout (int): 최대 실행 시간(초). 사용자가 별도로 지정하지 않으면 5 초가 기본값입니다.

    Returns:
        str: 표준 출력(stdout)과 표준 오류(stderr)을 합친 실행 결과 문자열.  
             출력이 없으면 "✅ 실행 완료 (출력 없음)"을 반환하며,  
             금지 모듈 탐지·타임아웃 발생 시에는 해당 사유를 안내하는 메시지를 반환합니다.
    """
}

GET_USER_LOCATION_CONST = {
    'no_location': "위치 정보 없음",
    'result_format': "현재 위치는 위도 {lat}, 경도 {lng}입니다.",
    'desc': """
    사용자의 현재 위치를 파악합니다. 사용자가 '내 위치' 또는 '현재 위치'와 같은 질문을 할 때 유용합니다.
    
    Args:
        query (str): 사용자의 질문이나 요청 (예: "내 위치가 어디야?", "현재 위치 알려줘")
    
    Returns:
        str: 사용자의 현재 위치 정보
    """,
}

NEARBY_SEARCH_CONST = {
    'no_result': "주변에 '{keyword}' 관련 장소가 없습니다.",
    'result_format': "{name} ({vicinity}) 평점 : {rating}",
    'desc': """
    사용자의 현재 위치를 기준으로 주변 장소를 검색합니다. 사용자가 '주변에 있는 카페', '내 근처의 음식점'과 같은 질문을 할 때 유용합니다.
    
    Args:
        keyword (str): 검색할 장소의 키워드 (예: "카페", "음식점")
        latlng (dict[str, float]): 사용자의 현재 위치 (위도와 경도)
        radius (int): 검색 반경 (미터 단위), 만약 사용자가 "1km 이내의 카페"라고 요청하면 1000을 입력합니다. 사용자가 반경을 명시하지 않으면 기본값은 200m입니다.
        
    Returns:
        str: 각 장소의 주소와 평점을 포함한 주변 장소 목록
    """
}

WEB_SEARCH_CONST = {
    'result_format': "{idx}번째 검색 결과\nTitle:   {title}\nURL:     {url}\nContent: {content}\n",
    'desc':"""
    웹 검색을 수행하고 상위 k개 결과를 문자열로 반환합니다. (default k=4)
    
    Args:
        query (str): 검색 쿼리 (예: '8월 12일자 미국 타임지의 뉴스 헤드라인', '사자성어 무위전변 뜻')
    
    Returns:
        str: 검색 결과 string. (예: '1번째 검색 결과\nTitle: ...\nURL: ...\nContent: ...\n\n2번째 검색 결과 ...')
    """,
}

GET_DATETIME_CONST = {
    'desc': """
    현재 날짜와 시간을 지정된 형식으로 반환합니다. 
    만약 유저가 날짜와 시간에 관련된 질문을 하거나, 최신 정보를 궁금해 할 때 유용합니다 (예: '현재 시간은 몇 시야?' '어제자 뉴스가 궁금해.').
    
    Args:
        query (str): 사용자의 질문이나 요청. (예: '현재 시간은 몇 시야?' '어제자 뉴스가 궁금해.')
        format (str): 필요한 datetime 정보의 형식. (예: "%Y-%m-%d %H:%M:%S", "%m-%d (%A)")
    
    Returns:
        str: `format`의 형식을 갖는 datetime string
    """
}

GET_IMAGE_FROM_SCREEN_CONST = {
    'desc': """
    Screenshot을 찍어 파일로 저장하고, 해당 파일의 경로를 리턴합니다.
    
    Args:
        query (str): 사용자의 질문이나 요청 (예: "지금 내가 보고 있는 화면을 찍어서 파일명을 말해줘.", "너도 지금 내가 보고 있는 영상 같이 보고 싶지? 현재 창 화면을 찍어봐")
    
    Returns:
        str: 방금 찍은 스크린샷의 파일 경로
    """
}

GET_IMAGE_FROM_DB_CONST = {
    'desc': """
    예전 대화에 사용되었던 사진을 다시 보고 싶을 때, 이 tool을 사용해 그 사진에 대한 설명이나 당시 메세지 기록을 query로 삼아 사진의 파일명을 얻어낼 수 있습니다.
    
    Args:
        query (str): 사진을 찾기 위한 쿼리 (예: "예전에 '슈퍼맨과 배트맨이 싸우고 있는 만화의 한 장면'이라고 반응했던 사진", "푸른색 바다 앞에서 강아지가 뛰놀고 있는 사진")
    
    Returns:
        str: 쿼리로 찾아낸 사진의 파일 경로. 만약 사진이 검색되지 않았거나 오류가 발생했다면 빈 string을 반환함.
    """,
    'not_found': "",
}

VISION_TOOL_CONST = {
    'desc': """
    사용자의 쿼리와 이미지를 동시에 활용해 응답합니다. 
    사용자가 사진 파일의 경로를 직접 포함해 질문하거나, 현재 맥락상 사진이 필요할 때 해당 사진의 경로와 함께 이 도구를 호출해 멀티모달 답변을 얻을 수 있습니다.
    
    Args:
        query (str): 사용자의 질문이나 요청 (예: "이 사진을 묘사해봐.", "이 그림의 왼쪽에 있는 캐릭터 이름이 뭐야?")
        iamge_path (str): 첨부 사진의 파일 경로
    Returns:
        str: 사용자 쿼리에 대한 (이미지를 활용한) 답변
    """
}

THOUGHT_CONST = {
    'desc': """
    이 tool은 special tool입니다. tool_input으로 tool을 직접 실행하는 것이 아닌, 'message' tool_input이 직접 당신의 생각으로써 기능합니다.
    이 tool은 만약 다른 어떤 tool도 사용하지 않을 때 발동할 의무가 있습니다. 현재 단계에서 사용자의 질문에 응답하기 위해 추가적인 생각이 필요할 때도 발동할 수 있습니다.
    이때, 당신의 생각은 'message'에 들어가야 하며, 그것이 바로 사용자에게 전달됩니다.
    
    Args:
        message (str): 당신의 생각.
    """
}

SAVE_CHAT_MEMORY_CONST = {
    'desc': """
    이 tool은 special tool입니다. 지금까지 유저와의 대화 기록을 영구히 저장하고 싶을 때 사용합니다.
    
    Args:
        message (str): 이 tool을 발동하게 된 사용자의 질문이나 요청 (예: '우리의 기억을 저장해줘.', '지금까지의 대화를 기록해두자.').
    """
}

CLEAR_CHAT_MEMORY_CONST = {
    'desc': """
    이 tool은 special tool입니다. 지금까지 유저와의 대화 기록을 삭제하거나 초기화하고 싶을 때 사용합니다.
    
    Args:
        message (str): 이 tool을 발동하게 된 사용자의 질문이나 요청 (예: '기억을 삭제해줘.', '지금까지의 대화 내역을 초기화해줘.')
    """
}
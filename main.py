import os
import requests
import json
from dotenv import load_dotenv
import sys
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}


def load_env():
    """加载环境变量"""
    print("=" * 50)
    print("开始加载环境变量...")
    load_dotenv()
    env = os.environ
    
    # 检查必要环境变量
    required_vars = ['BASE_URL', 'EMAIL', 'PASSWORD']
    missing_vars = [var for var in required_vars if var not in env or not env[var]]
    
    if missing_vars:
        print(f"❌ 缺少必要环境变量: {missing_vars}")
        print("请确保 .env 文件中包含以下变量:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    
    print("✅ 环境变量加载成功")
    print(f"BASE_URL: {env.get('BASE_URL', '未设置')}")
    print(f"EMAIL: {env.get('EMAIL', '未设置')}")
    print(f"PASSWORD: {'*' * len(env.get('PASSWORD', ''))} (长度: {len(env.get('PASSWORD', ''))})")
    return dict(env)


def login(url, email, password):
    """用户登录"""
    print("\n" + "=" * 50)
    print(f"开始登录...")
    print(f"登录URL: {url}")
    print(f"登录邮箱: {email}")
    
    # 根据浏览器请求，使用表单格式发送数据
    form_data = {
        'email': email,
        'password': password
    }
    
    # 使用表单格式的请求头
    request_headers = headers.copy()
    request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    request_headers['Origin'] = 'https://fljc.cc'
    request_headers['Referer'] = 'https://fljc.cc/auth/login'
    
    try:
        # 使用data参数发送表单数据
        response = requests.post(url=url, data=form_data, headers=request_headers, timeout=30)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 登录失败 - 状态码异常: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
        
        try:
            data = json.loads(response.text)
            
            # 根据浏览器请求成功的经验，响应中可能有auth_data
            if 'auth_data' in data:
                token = data['auth_data']
                print(f"✅ 登录成功 (auth_data)")
                print(f"获取到Token (前20位): {token[:20]}...")
                return token
            elif 'data' in data and 'auth_data' in data['data']:
                token = data['data']['auth_data']
                print(f"✅ 登录成功 (data.auth_data)")
                print(f"获取到Token (前20位): {token[:20]}...")
                return token
            elif 'data' in data and 'token' in data['data']:
                token = data['data']['token']
                print(f"✅ 登录成功 (data.token)")
                print(f"获取到Token (前20位): {token[:20]}...")
                return token
            elif 'token' in data:
                token = data['token']
                print(f"✅ 登录成功 (token)")
                print(f"获取到Token (前20位): {token[:20]}...")
                return token
            elif 'access_token' in data:
                token = data['access_token']
                print(f"✅ 登录成功 (access_token)")
                print(f"获取到Token (前20位): {token[:20]}...")
                return token
            else:
                print(f"❌ 登录失败 - 响应中未找到token或auth_data")
                print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 打印所有可能的字段
                print("响应中的所有字段:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ 登录失败 - JSON解析错误: {e}")
            print(f"原始响应: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 登录失败 - 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 登录失败 - 连接错误")
        return None
    except Exception as e:
        print(f"❌ 登录失败 - 未知错误: {e}")
        return None


def checkin(url, token):
    """执行签到"""
    print("\n" + "=" * 50)
    print("开始签到...")
    print(f"签到URL: {url}")
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    # 更新URL中的时间戳参数
    url = url.replace('t=1765504800371', f't={current_timestamp}')
    
    headers_copy = headers.copy()
    headers_copy['Access-Token'] = token
    headers_copy['Referer'] = 'https://fljc.cc/user'
    
    try:
        response = requests.post(url=url, headers=headers_copy, timeout=30)
        print(f"签到响应状态码: {response.status_code}")
        
        try:
            data = json.loads(response.text)
            print(f"签到响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'result' in data:
                print(f"✅ 签到结果: {data['result']}")
            elif 'msg' in data:
                print(f"✅ 签到消息: {data['msg']}")
            else:
                print(f"⚠️ 签到响应中未找到result或msg字段")
                
            # 如果有额外信息也打印出来
            if 'data' in data:
                print(f"签到数据: {data['data']}")
                
        except json.JSONDecodeError as e:
            print(f"❌ 签到响应解析失败: {e}")
            print(f"原始响应: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ 签到失败 - 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 签到失败 - 连接错误")
    except Exception as e:
        print(f"❌ 签到失败 - 未知错误: {e}")


def get_user_info(url, token):
    """获取用户信息"""
    print("\n" + "=" * 50)
    print("获取用户信息...")
    print(f"用户信息URL: {url}")
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    # 更新URL中的时间戳参数
    url = url.replace('t=1765504800371', f't={current_timestamp}')
    
    headers_copy = headers.copy()
    headers_copy['Access-Token'] = token
    headers_copy['Referer'] = 'https://fljc.cc/user'
    
    try:
        response = requests.get(url=url, headers=headers_copy, timeout=30)
        print(f"用户信息响应状态码: {response.status_code}")
        
        try:
            data = json.loads(response.text)
            print(f"用户信息响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'result' in data and 'data' in data['result']:
                user_data = data['result']['data']
                print("✅ 用户信息获取成功")
                
                # 打印关键用户信息
                if 'email' in user_data:
                    print(f"用户邮箱: {user_data.get('email')}")
                if 'plan' in user_data:
                    print(f"当前套餐: {user_data.get('plan')}")
                if 'plan_time' in user_data:
                    print(f"套餐到期时间: {user_data.get('plan_time')}")
                if 'money' in user_data:
                    print(f"账户余额: {user_data.get('money')}")
                if 'transfer_enable' in user_data:
                    total = int(user_data.get('transfer_enable', 0))
                    used = int(user_data.get('used', 0))
                    remaining = total - used
                    print(f"总流量: {total / 1024 / 1024 / 1024:.2f} GB")
                    print(f"已用流量: {used / 1024 / 1024 / 1024:.2f} GB")
                    print(f"剩余流量: {remaining / 1024 / 1024 / 1024:.2f} GB")
                if 'transfer_checkin' in user_data:
                    checkin_traffic = int(user_data.get('transfer_checkin', 0))
                    print(f"签到流量: {checkin_traffic / 1024 / 1024:.2f} MB")
                
                return user_data
            else:
                print("❌ 用户信息获取失败 - 响应格式异常")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ 用户信息响应解析失败: {e}")
            print(f"原始响应: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 获取用户信息失败 - 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 获取用户信息失败 - 连接错误")
        return None
    except Exception as e:
        print(f"❌ 获取用户信息失败 - 未知错误: {e}")
        return None


def convert_traffic(url, token, traffic):
    """转换流量"""
    print("\n" + "=" * 50)
    print("开始流量转换...")
    print(f"转换URL: {url}")
    print(f"转换流量: {traffic} MB")
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    # 更新URL中的时间戳参数
    url = url.replace('t=1765504800371', f't={current_timestamp}')
    
    headers_copy = headers.copy()
    headers_copy['Access-Token'] = token
    headers_copy['Referer'] = 'https://fljc.cc/user'
    
    # 对于流量转换，使用GET请求并传递参数
    params = {
        'traffic': str(traffic)
    }
    
    try:
        response = requests.get(url=url, headers=headers_copy, params=params, timeout=30)
        print(f"流量转换响应状态码: {response.status_code}")
        
        try:
            data = json.loads(response.text)
            print(f"流量转换响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'msg' in data:
                print(f"✅ 流量转换结果: {data['msg']}")
            elif 'result' in data:
                print(f"✅ 流量转换结果: {data['result']}")
            else:
                print(f"⚠️ 流量转换响应中未找到msg或result字段")
                
        except json.JSONDecodeError as e:
            print(f"❌ 流量转换响应解析失败: {e}")
            print(f"原始响应: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ 流量转换失败 - 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 流量转换失败 - 连接错误")
    except Exception as e:
        print(f"❌ 流量转换失败 - 未知错误: {e}")


def main():
    """主函数"""
    print("🚀 开始执行签到脚本")
    print("=" * 50)
    
    # 加载环境变量
    env = load_env()
    
    # 构建URL - 使用当前时间戳
    base_url = env['BASE_URL'].rstrip('/')
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    
    login_url = f"{base_url}/api/v1/passport/auth/login?t={current_timestamp}"
    checkin_url = f"{base_url}/api/v1/user/checkin?t={current_timestamp}"
    user_info_url = f"{base_url}/api/v1/user/info?t={current_timestamp}"
    convert_traffic_url = f"{base_url}/api/v1/user/koukanntraffic?t={current_timestamp}"
    
    email = env['EMAIL']
    password = env['PASSWORD']
    
    # 登录
    token = login(url=login_url, email=email, password=password)
    if token is None:
        print("\n❌ 登录失败，脚本终止")
        return
    
    # 签到
    checkin(url=checkin_url, token=token)
    
    # 获取用户信息
    data = get_user_info(url=user_info_url, token=token)
    if data is None:
        print("\n⚠️ 获取用户信息失败，跳过流量转换")
        return
    
    # 转换流量
    if 'transfer_checkin' in data:
        # 注意：transfer_checkin 单位是字节，转换为MB
        traffic_bytes = int(data['transfer_checkin'])
        traffic_mb = int(traffic_bytes / 1024 / 1024)
        print(f"\n📊 签到获得的剩余流量: {traffic_bytes} 字节 = {traffic_mb} MB")
        
        if traffic_mb > 0:
            convert_traffic(url=convert_traffic_url, token=token, traffic=traffic_mb)
        else:
            print("🎉 没有需要转换的流量，明天再来吧！")
    else:
        print("⚠️ 用户信息中未找到签到流量数据")
    
    print("\n" + "=" * 50)
    print("✅ 脚本执行完成")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()

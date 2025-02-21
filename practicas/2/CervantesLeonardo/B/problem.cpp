#include <bits/stdc++.h>
// #pragma GCC optimize("O3,unroll-loops")
// #pragma GCC target("avx2,bmi,bmi2,lzcnt,popcnt")
using namespace std;
#define pb push_back
#define ll long long
#define MOD 1000000007
#define INF 100000000
#define f first
#define s second

void solve() {
  
  string s;cin>>s;
  vector<vector<int>> v(26,vector<int>(26,0));
  set<int> st;
  st.insert(s[0]-'a');
  for(int i=1;i<s.size();i++){
    v[s[i-1]-'a'][s[i]-'a']++;
    st.insert(s[i]-'a');
  }
  vector<int> lt;
  for(auto u:st){
    lt.pb(u);
  }
  int k = lt.size();
  vector<int> dp((1<<k),INF);
  dp[0]=1;
  for(int i=0;i<(1<<k);i++){
    for(int j=0;j<k;j++){
      if((i&(1<<j))!=0)continue;
      int aux=dp[i]+v[lt[j]][lt[j]];
      for(int r=0;r<k;r++){
        if((i&(1<<r))!=0){
          aux+=v[lt[j]][lt[r]];
        }
      }
      dp[i+(1<<j)]=min(dp[i+(1<<j)],aux);
    }
  }
  cout<<dp[(1<<k)-1]<<endl;
  
}
int main() {
  ios_base::sync_with_stdio(false);  cin.tie(0);  cout.tie(0);
  // int t;cin>>t;for(int T=0;T<t;T++)
  solve();
}